from core.controllers import BaseControllers
from core.schemas import CommonsDependencies
from core.services import BaseServices

from . import schemas
from .services import move_services
from .config import settings

class MoveControllers(BaseControllers):
    def __init__(self, controller_name: str, service: BaseServices = None) -> None:
        super().__init__(controller_name, service)

    async def get_move_number(self, game_id: str):
        query = {"game_id": game_id}
        result = await self.get_all(query=query)
        return result['total_items'] + 1

    async def create(self, game_id: str, player_id: str, state: list, commons: CommonsDependencies) -> dict:
        data = {}
        data['game_id'] = game_id
        data['player_id'] = player_id
        data['state'] = state
        data['move_number'] = await self.get_move_number(game_id=game_id)   
        return await self.service.create(data=data, commons=commons)

    async def get_state_of_last_move(self, game_id: str):
        query = {"game_id": game_id}
        result = await self.get_all(query=query)
        if result['total_items'] > 0:
            return result['results'][0]['state']
        return settings.init_state
    
    async def move_back(self, game_id: str, commons: CommonsDependencies):
        # Step 1: Delete 2 previous moves
        query = {"game_id": game_id}
        results = await self.get_all(query=query)
        for move in results['results'][:2]:
            await self.soft_delete_by_id(_id=move['_id'], commons=commons)
        # Step 2: Get the state of the last moves
        return await self.get_state_of_last_move(game_id=game_id)

    async def is_current_move_of_player(self, game_id: str, player_id: str):
        query = {"game_id": game_id}
        result = await self.get_all(query=query)
        if result['total_items'] == 0:
            return True
        if result['results'][0]['player_id'] != player_id:
            return True
        return False
    
    async def edit(self, _id: str, data: schemas, commons: CommonsDependencies) -> dict:
        await self.get_by_id(_id=_id, commons=commons)
        data = data.model_dump(exclude_none=True)
        return await self.service.edit(_id=_id, data=data, commons=commons)

    async def get_all(self, query = None, search = None, search_in = None, page = 1, limit = 20, fields_limit = None, sort_by = "created_at", order_by = "desc", include_deleted = False, game_id: str = None, commons = None):
        if query and game_id is not None:
            query.update({
                "game_id": game_id
            })
        return await super().get_all(query, search, search_in, page, limit, fields_limit, sort_by, order_by, include_deleted, commons)

move_controllers = MoveControllers(controller_name="moves", service=move_services)
