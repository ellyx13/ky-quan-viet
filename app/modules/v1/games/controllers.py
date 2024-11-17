from core.controllers import BaseControllers
from core.schemas import CommonsDependencies
from core.services import BaseServices

from . import schemas
from .services import game_services
from .exceptions import ErrorCode as GameErrorCode
from .exceptions import ErrorCodeSocket as GameErrorCodeSocket
from .connection import manager
from fastapi import WebSocketDisconnect
from modules.v1.moves.controllers import move_controllers

class GameControllers(BaseControllers):
    def __init__(self, controller_name: str, service: BaseServices = None) -> None:
        super().__init__(controller_name, service)

    async def create(self, data: schemas.CreateRequest, commons: CommonsDependencies) -> dict:
        data = data.model_dump()
        return await self.service.create(data=data, commons=commons)

    async def edit(self, _id: str, data: schemas.EditRequest, commons: CommonsDependencies) -> dict:
        await self.get_by_id(_id=_id, commons=commons)
        data = data.model_dump(exclude_none=True)
        return await self.service.edit(_id=_id, data=data, commons=commons)

    async def get_all_games_public(self, query = None, search = None, search_in = None, page = 1, limit = 20, fields_limit = None, sort_by = "created_at", order_by = "desc", include_deleted = False, commons = None):
        if query is not None:
            query.update({
                "status": "waiting",
                "type": "public"
            })
        return await super().get_all(query, search, search_in, page, limit, fields_limit, sort_by, order_by, include_deleted, commons)

    async def get_by_code(self, code: str, commons: CommonsDependencies = None, ignore_error: bool = False) -> dict:
        return await self.service.get_by_code(code=code, commons=commons, ignore_error=ignore_error)

    async def get_by_room(self, websocket, game_id: str = None, game_code: str = None, commons: CommonsDependencies = None):
        if game_id:
            game = await self.get_by_id(_id=game_id, ignore_error=True)
        elif game_code:
            game = await self.get_by_code(code=game_code, ignore_error=True)
        else:
            await manager.raise_error(user_id=commons.current_user, error=GameErrorCodeSocket.RequiredFieldToJoinGame())
        if game is None:
            await manager.raise_error(user_id=commons.current_user, error=GameErrorCodeSocket.GameNotFound(game_id=game_id, game_code=game_code))
        return game

    async def get_other_player(self, game: dict, current_user: str):
        if game['host_id'] == current_user:
            return game['guest_id']
        elif game['guest_id'] == current_user:
            return game['host_id']
        
    def is_guest_in_game(self, game: dict, current_user: str):
        if game['guest_id'] == current_user:
            return True
        return False

    async def player_disconnected(self, game: dict, current_user: str):
        another_player = await self.get_other_player(game=game, current_user=current_user)
        await manager.send_data(user_id=another_player, data=GameErrorCodeSocket.YouWinBecauseOtherPlayerLeft())
        await manager.disconnect(user_id=current_user)
        
    async def game_is_ready_to_start(self, game: dict, commons: CommonsDependencies):
        await manager.send_data(user_id=commons.current_user, data=GameErrorCodeSocket.GameIsReadyToStart())
        await manager.send_data(user_id=game['host_id'], data=GameErrorCodeSocket.GameIsReadyToStart())
        
    async def waiting_for_other_player(self, user_id: str):
        await manager.send_data(user_id=user_id, data=GameErrorCodeSocket.WaitingForOtherPlayer())
    
    async def send_state_to_other_player(self, game: dict, state: list, commons: CommonsDependencies):
        data = {'state': state}
        other_player = await self.get_other_player(game=game, current_user=commons.current_user)
        await manager.send_data(user_id=other_player, data=data)
        
    async def get_next_turn(self, game: dict, current_user: str):
        if game['host_id'] == current_user:
            return "guest"
        elif game['guest_id'] == current_user:
            return "host"
        
    async def send_state_to_both_players(self, game: dict, state: list, commons: CommonsDependencies):
        data = {'state': state}
        data['turn'] = await self.get_next_turn(game=game, current_user=commons.current_user)
        other_player = await self.get_other_player(game=game, current_user=commons.current_user)
        await manager.send_data(user_id=other_player, data=data)
        await manager.send_data(user_id=commons.current_user, data=data)
        
    async def move_back(self, game: dict, commons: CommonsDependencies):
        state = await move_controllers.move_back(game_id=game['_id'], commons=commons)
        await self.send_state_to_both_players(game=game, state=state, commons=commons)
        
    async def verify_game(self, websocket, game_id: str = None, game_code: str = None, commons: CommonsDependencies = None):
        game = await self.get_by_room(websocket, game_id=game_id, game_code=game_code, commons=commons)
        if game['status'] not in ["pending", "waiting"]:
            await manager.raise_error(user_id=commons.current_user, error=GameErrorCodeSocket.GameIsNotAvailable(game_id=game_id))
            
        if game['status'] == "pending" and game['host_id'] == commons.current_user:
            await self.service.set_game_is_waiting(game_id=game["_id"])
            await self.waiting_for_other_player(user_id=commons.current_user)
        elif game['status'] == "waiting" and game['host_id'] != commons.current_user:
            await self.service.set_game_is_in_progress(game_id=game["_id"], guest_id=commons.current_user, commons=commons)
            await self.game_is_ready_to_start(game=game, commons=commons)
        elif game['status'] == "waiting" and game['host_id'] == commons.current_user:
            await self.waiting_for_other_player(user_id=commons.current_user)
        else:
            await manager.raise_error(user_id=commons.current_user, error=GameErrorCodeSocket.CanNotJoinGame())
        return game
            
    async def is_win(self, state: list):
        return all(item == "" for item in state[:12])
        
    async def notify_winner(self, game: dict, winner_id: str):
        lost_id = await self.get_other_player(game=game, current_user=winner_id)
        await manager.send_data(user_id=winner_id, data=GameErrorCodeSocket.YouWin())
        await manager.send_data(user_id=lost_id, data=GameErrorCodeSocket.YouLost())
        await manager.disconnect(user_id=winner_id)
        await manager.disconnect(user_id=lost_id)
        
    async def join_room(self, websocket, game_id: str = None, game_code: str = None, commons: CommonsDependencies = None):
        await manager.connect(commons.current_user, websocket)
        game = await self.verify_game(websocket, game_id=game_id, game_code=game_code, commons=commons)
        is_win = False
        try:
            while True:
                data = await websocket.receive_text()
                game = await self.get_by_room(websocket, game_id=game_id, game_code=game_code)
                is_game_ready = await self.service.is_game_ready(game_id=game["_id"])
                if is_game_ready is False:
                    await self.waiting_for_other_player(user_id=commons.current_user)
                    continue
                is_current_move_of_player = await move_controllers.is_current_move_of_player(game_id=game["_id"], player_id=commons.current_user)
                if is_current_move_of_player is False:
                    await manager.send_data(user_id=commons.current_user, data=GameErrorCodeSocket.NotYourTurn())
                    continue
                data = manager.parse_dict(data)
                if data.get('action') == "move_back":
                    await self.move_back(game=game, commons=commons)
                elif data.get('state'):
                    await move_controllers.create(game_id=game["_id"], player_id=commons.current_user, state=data["state"], commons=commons)
                    await self.send_state_to_other_player(game=game, state=data["state"], commons=commons)
                    is_win = await self.is_win(data["state"])
                    if is_win is True:
                        await self.service.set_game_is_completed(game_id=game["_id"], winner_id=commons.current_user, commons=commons)
                        await self.notify_winner(game=game, winner_id=commons.current_user)
                        return
        except WebSocketDisconnect:
            game = await self.get_by_room(websocket, game_id=game_id, game_code=game_code)
            if game["status"] == "completed":
                return
            other_player = await self.get_other_player(game=game, current_user=commons.current_user)
            await self.service.set_game_is_completed(game_id=game["_id"], winner_id=other_player, commons=commons)
            await self.player_disconnected(game=game, current_user=commons.current_user)
            return

game_controllers = GameControllers(controller_name="games", service=game_services)

