from core.controllers import BaseControllers
from core.schemas import CommonsDependencies
from core.services import BaseServices

from . import schemas
from .services import game_services
from .exceptions import ErrorCode as GameErrorCode
from .exceptions import ErrorCodeSocket as GameErrorCodeSocket
from .connection import manager
from fastapi import WebSocketDisconnect

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
            game = await self.get_by_id(_id=game_id, commons=commons, ignore_error=True)
        elif game_code:
            game = await self.get_by_code(code=game_code, commons=commons, ignore_error=True)
        else:
            await manager.raise_error(user_id=commons.current_user, error=GameErrorCodeSocket.RequiredFieldToJoinGame())
        if game is None:
            await manager.raise_error(user_id=commons.current_user, error=GameErrorCodeSocket.GameNotFound())
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

    async def player_disconnected(self, game: dict, current_user: str, is_close=True):
        another_player = await self.get_other_player(game=game, current_user=current_user)
        player = "Guest" if self.is_guest_in_game(game=game, current_user=current_user) else "Host"
        data = {"message": f"{player} has left the game."}
        await manager.send_data(user_id=another_player, data=data)
        await manager.disconnect(user_id=current_user, is_close=is_close)
        
    async def game_is_ready_to_start(self, game: dict, commons: CommonsDependencies):
        message = "Game is ready. You can start playing."
        await manager.send_message(user_id=commons.current_user, message=message)
        await manager.send_message(user_id=game['host_id'], message=message)
        
    async def waiting_for_other_player(self, user_id: str):
        await manager.send_message(user_id=user_id, message="Waiting for other player to join.")
        
    async def join_room(self, websocket, game_id: str = None, game_code: str = None, commons: CommonsDependencies = None):
        await manager.connect(commons.current_user, websocket)

        game = await self.get_by_room(websocket, game_id=game_id, game_code=game_code)
        if game is None or game['status'] not in ["pending", "waiting"]:
            await manager.raise_error(user_id=commons.current_user, error=GameErrorCodeSocket.GameIsNotAvailable(game_id=game_id))
            return await self.player_disconnected(game=game, current_user=commons.current_user)
        
        await self.service.add_game_to_managers(game_id=game["_id"], host_id=game["host_id"])
        print(game)
        if game['status'] == "pending" and game['host_id'] == commons.current_user:
            await self.service.set_game_is_waiting(game_id=game["_id"])
            await self.waiting_for_other_player(user_id=commons.current_user)
        elif game['status'] == "waiting" and game['host_id'] != commons.current_user:
            await self.service.set_game_is_in_progress(game_id=game["_id"], guest_id=commons.current_user)
            await self.game_is_ready_to_start(game=game, commons=commons)
        elif game['status'] == "waiting" and game['host_id'] == commons.current_user:
            await self.waiting_for_other_player(user_id=commons.current_user)
        else:
            await manager.raise_error(user_id=commons.current_user, error=GameErrorCodeSocket.CanNotJoinGame())
            return await self.player_disconnected(game=game, current_user=commons.current_user)
            
        try:
            while True:
                data = await websocket.receive_text()
                game = await self.get_by_room(websocket, game_id=game_id, game_code=game_code)
                is_game_ready = await self.service.is_game_ready(game_id=game["_id"])
                if is_game_ready is False:
                    await self.waiting_for_other_player(user_id=commons.current_user)
                data = manager.parse_dict(data)
                other_player = await self.get_other_player(game=game, current_user=commons.current_user)
                await manager.send_data(user_id=other_player, data=data)
        except WebSocketDisconnect:
            await self.player_disconnected(game=game, current_user=commons.current_user, is_close=False)
        

game_controllers = GameControllers(controller_name="games", service=game_services)
