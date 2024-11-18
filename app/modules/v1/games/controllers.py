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
from modules.v1.minimax.services import find_best_move
from users.controllers import user_controllers

class GameControllers(BaseControllers):
    def __init__(self, controller_name: str, service: BaseServices = None) -> None:
        super().__init__(controller_name, service)

    async def create(self, data: schemas.CreateRequest, commons: CommonsDependencies) -> dict:
        data = data.model_dump()
        return await self.service.create(data=data, commons=commons)
    
    async def get_total_game_of_user(self, user_id: str) -> list:
        query = {"$or": [{"host_id": user_id}, {"guest_id": user_id}]}
        results = await self.get_all(query=query)
        return results['total_items']
    
    async def get_name(self, game_id: str) -> dict:
        result = await self.get_by_id(_id=game_id)
        return result['name']
    
    async def get_guest_name(self, game_id: str) -> str | None:
        result = await self.get_by_id(_id=game_id)
        guest_id = result['guest_id']
        if guest_id is None:
            return None
        if guest_id == "AI":
            return "AI"
        return await user_controllers.get_name(user_id=guest_id)

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
        return current_user
    
    def is_guest_in_game(self, game: dict, current_user: str):
        if game['guest_id'] == current_user:
            return True
        return False

    async def player_disconnected(self, game: dict, current_user: str, is_room_ai: bool = False):
        if is_room_ai is True:
            await manager.disconnect(user_id=current_user)
        else:
            other_player = await self.get_other_player(game=game, current_user=current_user)
            await manager.send_data(user_id=other_player, data=GameErrorCodeSocket.YouWinBecauseOtherPlayerLeft())
            await manager.disconnect(user_id=current_user)
        
    async def game_is_ready_to_start(self, game: dict, commons: CommonsDependencies, is_room_ai: bool = False):
        if is_room_ai is True:
            await manager.send_data(user_id=commons.current_user, data=GameErrorCodeSocket.GameIsReadyToStart())
        else:
            player_info = {}
            player_info['host_id'] = game['host_id']
            player_info['guest_id'] = game['guest_id']
            player_info['host_name'] = await user_controllers.get_name(user_id=game['host_id'])
            player_info['guest_name'] = await user_controllers.get_name(user_id=game['guest_id'])
            await manager.send_data(user_id=commons.current_user, data=GameErrorCodeSocket.GameIsReadyToStart(player_info))
            await manager.send_data(user_id=game['host_id'], data=GameErrorCodeSocket.GameIsReadyToStart(player_info))
        
    async def waiting_for_other_player(self, user_id: str):
        await manager.send_data(user_id=user_id, data=GameErrorCodeSocket.WaitingForOtherPlayer())
    
    async def send_state_to_other_player(self, game: dict, data: dict, commons: CommonsDependencies, is_room_ai: bool = False):
        if is_room_ai is False:
            data['turn'] = await self.get_next_turn(game=game, current_user=commons.current_user, is_room_ai=is_room_ai)
            other_player = await self.get_other_player(game=game, current_user=commons.current_user)
            await manager.send_data(user_id=other_player, data=data)
        else:
            data['turn'] = await self.get_next_turn(game=game, current_user=commons.current_user, is_room_ai=is_room_ai)
            # Current user in room AI is always host
            await manager.send_data(user_id=commons.current_user, data=data)
        
    async def get_next_turn(self, game: dict, current_user: str, is_move_back: bool = False, is_room_ai: bool = False):
        if is_room_ai is True:
            return "AI"
        if game['host_id'] == current_user:
            return "guest" if is_move_back is False else "host"
        elif game['guest_id'] == current_user:
            return "host" if is_move_back is False else "guest"
            
    async def send_state_to_both_players(self, game: dict, state: list, commons: CommonsDependencies):
        data = {'state': state}
        data['turn'] = await self.get_next_turn(game=game, current_user=commons.current_user, is_move_back=True)
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
            game = await self.service.set_game_is_waiting(game_id=game["_id"])
            await self.waiting_for_other_player(user_id=commons.current_user)
        elif game['status'] == "waiting" and game['host_id'] != commons.current_user:
            game = await self.service.set_game_is_in_progress(game_id=game["_id"], guest_id=commons.current_user, commons=commons)
            await self.game_is_ready_to_start(game=game, commons=commons, is_room_ai=False)
        elif game['status'] == "waiting" and game['host_id'] == commons.current_user:
            await self.waiting_for_other_player(user_id=commons.current_user)
        else:
            await manager.raise_error(user_id=commons.current_user, error=GameErrorCodeSocket.CanNotJoinGame())
        return game
            
    async def is_win(self, state: list):
        if state[0] == "" and state[6] == "":
            return True
        return False
        
    async def notify_winner(self, game: dict, winner_id: str, is_room_ai: bool = False):
        if is_room_ai is True:
            if winner_id == "AI":
                await manager.send_data(user_id=game['host_id'], data=GameErrorCodeSocket.YouLost())
                await manager.disconnect(user_id=game['host_id'])
            else:
                await manager.send_data(user_id=game['host_id'], data=GameErrorCodeSocket.YouWin())
                await manager.disconnect(user_id=game['host_id'])
        else:
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
                    await self.send_state_to_other_player(game=game, data=data, commons=commons, is_room_ai=False)
                    is_win = await self.is_win(data["state"])
                    if is_win is True:
                        await self.service.set_game_is_completed(game_id=game["_id"], winner_id=commons.current_user, commons=commons)
                        await self.notify_winner(game=game, winner_id=commons.current_user)
                        return
        except WebSocketDisconnect:
            game = await self.get_by_room(websocket, game_id=game_id, game_code=game_code, commons=commons)
            if game["status"] == "completed":
                return
            other_player = await self.get_other_player(game=game, current_user=commons.current_user)
            await self.service.set_game_is_completed(game_id=game["_id"], winner_id=other_player, commons=commons)
            await self.player_disconnected(game=game, current_user=commons.current_user)
            return
        
    async def verify_game_ai(self, websocket, game_id: str = None, game_code: str = None, commons: CommonsDependencies = None):
        game = await self.get_by_room(websocket, game_id=game_id, game_code=game_code, commons=commons)
        if game['status'] not in ["pending", "waiting"]:
            await manager.raise_error(user_id=commons.current_user, error=GameErrorCodeSocket.GameIsNotAvailable(game_id=game_id))
            
        if game['is_guest_ai'] is False:
            await manager.raise_error(user_id=commons.current_user, error=GameErrorCodeSocket.IsNotRoomAI())
        
        if game['host_id'] != commons.current_user:
            await manager.raise_error(user_id=commons.current_user, error=GameErrorCodeSocket.YouAreNotHostInRoom())
            
        await self.service.set_game_is_in_progress(game_id=game["_id"], commons=commons)
        await self.game_is_ready_to_start(game=game, commons=commons, is_room_ai=True)
        return game
    
    
    async def join_room_ai(self, websocket, game_id: str = None, game_code: str = None, commons: CommonsDependencies = None):
        await manager.connect(commons.current_user, websocket)
        game = await self.verify_game_ai(websocket, game_id=game_id, game_code=game_code, commons=commons)
        game_level = game.get('level', 'easy')
        is_win = False
        player = commons.current_user
        try:
            while True:
                if player == "AI":
                    data = await find_best_move(state=data['state'], game_level=game_level)
                else:
                    data = await websocket.receive_text()
                game = await self.get_by_room(websocket, game_id=game_id, game_code=game_code)
                is_game_ready = await self.service.is_game_ready(game_id=game["_id"])
                if is_game_ready is False:
                    await self.waiting_for_other_player(user_id=player)
                    continue
                is_current_move_of_player = await move_controllers.is_current_move_of_player(game_id=game["_id"], player_id=player)
                if is_current_move_of_player is False:
                    await manager.send_data(user_id=player, data=GameErrorCodeSocket.NotYourTurn())
                    continue
                if player != "AI":
                    data = manager.parse_dict(data)
                await move_controllers.create(game_id=game["_id"], player_id=player, state=data["state"], commons=commons)
                if player == "AI":
                    await self.send_state_to_other_player(game=game, data=data, commons=commons, is_room_ai=True)
                is_win = await self.is_win(data["state"])
                if is_win is True:
                    await self.service.set_game_is_completed(game_id=game["_id"], winner_id=player, commons=commons)
                    await self.notify_winner(game=game, winner_id=player, is_room_ai=True)
                    return
                player = "AI" if player == commons.current_user else commons.current_user
        except WebSocketDisconnect:
            game = await self.get_by_room(websocket, game_id=game_id, game_code=game_code, commons=commons)
            if game["status"] == "completed":
                return
            await self.service.set_game_is_completed(game_id=game["_id"], winner_id="AI", commons=commons)
            await self.player_disconnected(game=game, current_user=commons.current_user, is_room_ai=True)
            return

game_controllers = GameControllers(controller_name="games", service=game_services)

