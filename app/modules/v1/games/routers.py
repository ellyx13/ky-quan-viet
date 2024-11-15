from core.schemas import CommonsDependencies, ObjectIdStr, PaginationParams
from fastapi import Depends
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter

from . import schemas
from .controllers import game_controllers
from .services import game_services

router = InferringRouter(
    prefix="/v1",
    tags=["v1/games"],
)


@cbv(router)
class RoutersCBV:
    commons: CommonsDependencies = Depends(CommonsDependencies)  # type: ignore

    @router.get("/users/me/games", status_code=200, responses={200: {"model": schemas.ListResponse, "description": "Get games success"}})
    async def get_all_games_status(self, pagination: PaginationParams = Depends()):
        search_in = ["name", "code"]
        results = await game_controllers.get_all_games_status(
            query=pagination.query,
            search=pagination.search,
            search_in=search_in,
            page=pagination.page,
            limit=pagination.limit,
            fields_limit=pagination.fields,
            sort_by=pagination.sort_by,
            order_by=pagination.order_by,
            commons=self.commons,
        )
        if pagination.fields:
            return results
        return schemas.ListResponse(**results)
    
    @router.get("/games/public", status_code=200, responses={200: {"model": schemas.ListResponse, "description": "Get games public success"}})
    async def get_all_games_public(self, pagination: PaginationParams = Depends()):
        search_in = ["name", "code"]
        results = await game_controllers.get_all_games_public(
            query=pagination.query,
            search=pagination.search,
            search_in=search_in,
            page=pagination.page,
            limit=pagination.limit,
            fields_limit=pagination.fields,
            sort_by=pagination.sort_by,
            order_by=pagination.order_by,
            commons=self.commons,
        )
        if pagination.fields:
            return results
        return schemas.ListResponse(**results)

    @router.get("/games", status_code=200, responses={200: {"model": schemas.ListResponse, "description": "Get games success"}})
    async def get_all(self, pagination: PaginationParams = Depends()):
        search_in = ["name", "code"]
        results = await game_controllers.get_all(
            query=pagination.query,
            search=pagination.search,
            search_in=search_in,
            page=pagination.page,
            limit=pagination.limit,
            fields_limit=pagination.fields,
            sort_by=pagination.sort_by,
            order_by=pagination.order_by,
            commons=self.commons,
        )
        if pagination.fields:
            return results
        return schemas.ListResponse(**results)

    @router.get("/games/{_id}", status_code=200, responses={200: {"model": schemas.Response, "description": "Get game success"}})
    async def get_detail(self, _id: ObjectIdStr, fields: str = None):
        results = await game_controllers.get_by_id(_id=_id, fields_limit=fields, commons=self.commons)
        if fields:
            return results
        return schemas.Response(**results)

    @router.post("/games", status_code=201, responses={201: {"model": schemas.Response, "description": "Create game success"}})
    async def create(self, data: schemas.CreateRequest):
        result = await game_controllers.create(data=data, commons=self.commons)
        return schemas.Response(**result)

    @router.put("/games/{_id}", status_code=200, responses={200: {"model": schemas.Response, "description": "Update game success"}})
    async def edit(self, _id: ObjectIdStr, data: schemas.EditRequest):
        results = await game_controllers.edit(_id=_id, data=data, commons=self.commons)
        return schemas.Response(**results)

    @router.delete("/games/{_id}", status_code=204)
    async def delete(self, _id: ObjectIdStr):
        results = await game_controllers.soft_delete_by_id(_id=_id, commons=self.commons)