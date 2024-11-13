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
    
    # Overload function get_all of history, this function just get_all of games have user join game and completed game.
    async def get_all(self, query = None, search = None, search_in = None, page = 1, limit = 20, fields_limit = None, sort_by = "created_at", order_by = "desc", include_deleted = False, user_id: str = None,commons = None):
        query_game = ({
            "$or":[
                {"host_id": user_id},
                {"guest_id": user_id}
            ]
        })
        data_games = await game_controllers.get_all(query=query_game)

        games_id = []
        for data in data_games["results"]:
            game_id = data["_id"]
            games_id.append(game_id)

        query = ({
            "game_id": {"$in": games_id}
        })
        return await super().get_all(query, search, search_in, page, limit, fields_limit, sort_by, order_by, include_deleted, commons)
    

history_controllers = HistoryControllers(controller_name="history", service=history_services)
