from core.schemas import CommonsDependencies
from core.services import BaseServices
from db.base import BaseCRUD
from db.engine import app_engine

from . import models, schemas
from .exceptions import ErrorCode as GameErrorCode 
import random


class GameManagers:
    def __init__(self) -> None:
        self.manager = {}

    def add_game(self, game_id: str, host_id: str):
        data = {'status': 'pending', 'host_id': host_id}
        self.manager[game_id] = data

    def set_game_is_waiting(self, game_id: str):
        self.manager[game_id]['status'] = "waiting"

    def set_game_is_in_progress(self, game_id: str, guest_id: str):
        self.manager[game_id]["status"] = "in_progress"
        self.manager[game_id]["guest_id"] = guest_id

    def is_game_ready(self, game_id: str):
        game = self.manager.get(game_id, {})
        if game['status'] == "in_progress":
            return game
        return False

class GameServices(BaseServices):
    def __init__(self, service_name: str, managers: GameManagers, crud: BaseCRUD = None) -> None:
        super().__init__(service_name, crud)
        self.managers = managers
        
    async def create(self, data: schemas.CreateRequest, commons: CommonsDependencies) -> dict:
        generate_code = await self.generate_code()
        data["code"] = generate_code
        data["status"] = "pending"
        data["created_by"] = data["host_id"] = self.get_current_user(commons=commons)
        data["created_at"] = self.get_current_datetime()
        data_save = models.Games(**data).model_dump()
        # Check if the user has already created a game, they will not be allowed to create another one.
        data_check = await self.crud.get_by_field(data=data_save["host_id"], field_name="host_id")
        if data_check:
            for record in data_check:
                if record["status"] in ["waiting" ,"in_progress"]:
                    raise GameErrorCode.AlreadyGame()
        result = await self.save_unique(data=data_save, unique_field="code")
        self.managers.add_manager(game_id=result["_id"], host_id=result["host_id"])
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
            result[0]
        return None

    async def add_game_to_managers(self, game_id: str, host_id: str):
        self.managers.add_game(game_id=game_id, host_id=host_id)
        
    async def set_game_is_waiting(self, game_id: str) -> dict:
        data_update = {}
        data_update["status"] = "waiting"
        result = await self.update_by_id(_id=game_id, data=data_update)
        self.managers.set_game_is_waiting(game_id=game_id)
        return result
    
    async def set_game_is_in_progress(self, game_id: str, guest_id: str) -> dict:
        data_update = {}
        data_update["status"] = "in_progress"
        data_update["guest_id"] = guest_id
        print(data_update)
        result = await self.update_by_id(_id=game_id, data=data_update)
        print(result)
        self.managers.set_game_is_in_progress(game_id=game_id, guest_id=guest_id)
        return result
    
    async def is_game_ready(self, game_id: str):
        return self.managers.is_game_ready(game_id=game_id)
    
game_crud = BaseCRUD(database_engine=app_engine, collection="games")
game_managers = GameManagers()
game_services = GameServices(service_name="games", crud=game_crud, managers=game_managers)