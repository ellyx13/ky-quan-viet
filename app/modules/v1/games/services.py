from core.schemas import CommonsDependencies
from core.services import BaseServices
from db.base import BaseCRUD
from db.engine import app_engine

from . import models, schemas
from .exceptions import ErrorCode as GameErrorCode 
import random
from modules.v1.histories.services import history_services
from users.services import user_services

class GameServices(BaseServices):
    def __init__(self, service_name: str, crud: BaseCRUD = None) -> None:
        super().__init__(service_name, crud)
        
    async def create(self, data: schemas.CreateRequest, commons: CommonsDependencies) -> dict:
        generate_code = await self.generate_code()
        data["code"] = generate_code
        data["status"] = "pending"
        data["created_by"] = data["host_id"] = self.get_current_user(commons=commons)
        data["created_at"] = self.get_current_datetime()
        data_save = models.Games(**data).model_dump()
        # Check if the user has already created a game, they will not be allowed to create another one.
        data_check = await self.get_by_field(data=data_save["host_id"], field_name="host_id", ignore_error=True)
        if data_check:
            for record in data_check:
                if record["status"] in ["pending", "waiting", "in_progress"]:
                    raise GameErrorCode.AlreadyGame()
        result = await self.save_unique(data=data_save, unique_field="code")
        return result
    
    async def edit(self, _id: str, data: schemas.EditRequest, commons: CommonsDependencies) -> dict:
        data["updated_by"] = self.get_current_user(commons=commons)
        data["updated_at"] = self.get_current_datetime()
        return await self.update_by_id(_id=_id, data=data)

    async def generate_code(self) -> str:
        while True:
            code = random.randint(100000, 999999)
            check_code = await self.crud.get_by_field(data=code, field_name="code")
            if not check_code:
                return code

    async def get_by_code(self, code: str, commons: CommonsDependencies = None, ignore_error: bool = False) -> dict | None:
        result = await self.get_by_field(data=code, field_name="code", commons=commons, ignore_error=ignore_error)
        if result:
            return result[0]
        return None
        
    async def set_game_is_waiting(self, game_id: str) -> dict:
        data_update = {}
        data_update["status"] = "waiting"
        result = await self.update_by_id(_id=game_id, data=data_update)
        return result
    
    async def set_game_is_in_progress(self, game_id: str, commons: CommonsDependencies, guest_id: str = None) -> dict:
        data_update = {}
        data_update['start_at'] = self.get_current_datetime()
        data_update["status"] = "in_progress"
        if guest_id:
            data_update["guest_id"] = guest_id
        result = await self.edit(_id=game_id, data=data_update, commons=commons)
        return result
    
    async def is_game_ready(self, game_id: str):
        game = await self.get_by_id(_id=game_id)
        if game["status"] == "in_progress":
            return game
        return False
    
    async def set_game_is_completed(self, game_id: str, winner_id: str, commons: CommonsDependencies) -> dict:
        game = await self.get_by_id(_id=game_id)
        data_update = {}
        data_update["status"] = "completed"
        data_update["end_at"] = self.get_current_datetime()
        try:
            duration = int((data_update["end_at"] - game["start_at"]).total_seconds())
        except Exception:
            duration = 120
        result = await self.edit(_id=game_id, data=data_update, commons=commons)
        await history_services.create(game_id=game_id, winner_id=winner_id, duration=duration, commons=commons)
        if winner_id != "AI":
            await user_services.increase_score(user_id=winner_id, commons=commons)
        return result
    
game_crud = BaseCRUD(database_engine=app_engine, collection="games")
game_services = GameServices(service_name="games", crud=game_crud)