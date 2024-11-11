from core.schemas import CommonsDependencies
from core.services import BaseServices
from db.base import BaseCRUD
from db.engine import app_engine

from . import models, schemas
from .exceptions import ErrorCode as GameErrorCode 
import random


class GameServices(BaseServices):
    def __init__(self, service_name: str, crud: BaseCRUD = None) -> None:
        super().__init__(service_name, crud)

    async def create(self, data: schemas.CreateRequest, commons: CommonsDependencies) -> dict:
        generate_code = await self.generate_code()
        data["code"] = generate_code
        data["status"] = "waiting"
        data["created_by"] = data["host_id"] = self.get_current_user(commons=commons)
        data["created_at"] = self.get_current_datetime()
        data_save = models.Games(**data).model_dump()
        # Check if the user has already created a game, they will not be allowed to create another one.
        data_check = await self.crud.get_by_field(data=data_save["host_id"], field_name="host_id")
        if data_check:
            for record in data_check:
                if record["status"] in ["waiting" ,"in_progress"]:
                    raise GameErrorCode.AlreadyGame()
        return await self.save_unique(data=data_save, unique_field="code")
    
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


game_crud = BaseCRUD(database_engine=app_engine, collection="games")
game_services = GameServices(service_name="games", crud=game_crud)
