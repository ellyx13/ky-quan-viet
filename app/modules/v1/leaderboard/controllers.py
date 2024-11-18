from core.controllers import BaseControllers
from core.services import BaseServices

from users.controllers import user_controllers
from modules.v1.histories.controllers import history_controllers

class LeaderboardControllers(BaseControllers):
    def __init__(self, controller_name: str, service: BaseServices = None) -> None:
        super().__init__(controller_name, service)

    
    # Overload function get_all of history, this function just get_all of games have user join game and completed game.
    async def get_all(self, query = None, search = None, search_in = None, page = 1, limit = 20, fields_limit = None, sort_by = "score", order_by = "desc", include_deleted = False, commons = None):
        if query is None:
            query = {}
            query['score'] = ['$ne', None]
        else:
            query.update({'score': {'$ne': None}})
        results = await user_controllers.get_all(query=query, search=search, search_in=search_in, page=page, limit=limit, fields_limit=fields_limit, sort_by=sort_by, order_by=order_by, include_deleted=include_deleted, commons=commons)
        for result in results["results"]:
            result['total_win'] = await history_controllers.get_total_game_win(user_id=result['_id'])
            result['total_lose'] = await history_controllers.get_total_game_lose(user_id=result['_id'])
        return results

leaderboard_controllers = LeaderboardControllers(controller_name="leaderboard")
