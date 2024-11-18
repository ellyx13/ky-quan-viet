from core.schemas import CommonsDependencies, ObjectIdStr, PaginationParams
from fastapi import Depends
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter

from . import schemas
from .controllers import history_controllers
from ..games.controllers import game_controllers

router = InferringRouter(
    prefix="/v1",
    tags=["v1/histories"],
)


@cbv(router)
class RoutersCBV:
    commons: CommonsDependencies = Depends(CommonsDependencies)  # type: ignore

    @router.get("/users/me/histories", status_code=200, responses={200: {"model": schemas.ListResponse, "description": "Get histories success"}})
    async def get_all(self, pagination: PaginationParams = Depends()):
        search_in = []
        results = await history_controllers.get_all(
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

