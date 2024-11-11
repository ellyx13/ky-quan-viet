from core.controllers import BaseControllers
from core.schemas import CommonsDependencies
from core.services import BaseServices

from . import schemas
from .services import history_services


class HistoryControllers(BaseControllers):
    def __init__(self, controller_name: str, service: BaseServices = None) -> None:
        super().__init__(controller_name, service)

    async def create(self, data: schemas.CreateRequest, commons: CommonsDependencies) -> dict:
        data = data.model_dump()
        return await self.service.create(data=data, commons=commons)

    # async def edit(self, _id: str, data: schemas.EditRequest, commons: CommonsDependencies) -> dict:
    #     await self.get_by_id(_id=_id, commons=commons)
    #     data = data.model_dump(exclude_none=True)
    #     return await self.service.edit(_id=_id, data=data, commons=commons)


history_controllers = HistoryControllers(controller_name="history", service=history_services)
