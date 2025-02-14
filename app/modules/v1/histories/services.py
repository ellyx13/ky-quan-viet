from core.schemas import CommonsDependencies
from core.services import BaseServices
from db.base import BaseCRUD
from db.engine import app_engine

from . import models
from .config import settings

class HistoryServices(BaseServices):
    def __init__(self, service_name: str, crud: BaseCRUD = None) -> None:
        super().__init__(service_name, crud)

    async def create(self, game_id: str, winner_id: str, duration: int, commons: CommonsDependencies) -> dict:
        data = {}
        data['game_id'] = game_id
        data['winner'] = winner_id
        data['duration'] = duration
        data['score'] = settings.default_score
        data["created_by"] = self.get_current_user(commons=commons)
        data["created_at"] = self.get_current_datetime()
        data_save = models.Histories(**data).model_dump()
        return await self.save(data=data_save)


history_crud = BaseCRUD(database_engine=app_engine, collection="histories")
history_services = HistoryServices(service_name="histories", crud=history_crud)
