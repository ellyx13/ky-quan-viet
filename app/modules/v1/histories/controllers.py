from core.controllers import BaseControllers
from core.schemas import CommonsDependencies
from core.services import BaseServices

from . import schemas
from .services import history_services
from ..games.controllers import game_controllers

class HistoryControllers(BaseControllers):
    def __init__(self, controller_name: str, service: BaseServices = None) -> None:
        super().__init__(controller_name, service)

    async def create(self, data: schemas, commons: CommonsDependencies) -> dict:
        data = data.model_dump()
        return await self.service.create(data=data, commons=commons)
    
    async def is_host_win(self, game_id: str, winner) -> bool:
        game = await game_controllers.get_by_id(game_id)
        if game['host_id'] == winner:
            return True
        return False 
    
    # Overload function get_all of history, this function just get_all of games have user join game and completed game.
    async def get_all(self, query = None, search = None, search_in = None, page = 1, limit = 20, fields_limit = None, sort_by = "created_at", order_by = "desc", include_deleted = False, commons = None):
        current_user = self.get_current_user(commons=commons)
        query_game = {}
        query_game['$or'] = [{"host_id": current_user}, {"guest_id": current_user}]
        games = await game_controllers.get_all(query=query_game)

        games_id = []
        for game in games["results"]:
            games_id.append(game['_id'])

        new_query = {"game_id": {"$in": games_id}}
        histories = await super().get_all(new_query, search, search_in, page, limit, fields_limit, sort_by, order_by, include_deleted, commons)
        for history in histories["results"]:
            history['game_name'] = await game_controllers.get_name(game_id=history['game_id'])
            history['guest_name'] = await game_controllers.get_guest_name(game_id=history['game_id'])
            history['is_host_win'] = await self.is_host_win(game_id=history['game_id'], winner=history['winner'])
        return histories
    
    async def get_total_game_win(self, user_id: str) -> int:
        query = {"winner": user_id}
        results = await game_controllers.get_all(query=query)
        return results['total_items']
    
    async def get_total_game_lose(self, user_id: str) -> int:
        total_games = await game_controllers.get_total_game_of_user(user_id=user_id)
        total_win = await self.get_total_game_win(user_id=user_id)
        return total_games - total_win
    

history_controllers = HistoryControllers(controller_name="history", service=history_services)
