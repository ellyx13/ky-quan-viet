from core.schemas import CommonsDependencies
from fastapi import Depends
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter

from . import schemas
from .controllers import leaderboard_controllers

router = InferringRouter(
    prefix="/v1",
    tags=["v1/leaderboard"],
)


@cbv(router)
class RoutersCBV:
    commons: CommonsDependencies = Depends(CommonsDependencies)  # type: ignore

    @router.get("/leaderboard", status_code=200, responses={200: {"model": schemas.ListResponse, "description": "Get histories success"}})
    async def get_all(self, pagination: schemas.PaginationParams = Depends()):
        search_in = []
        results = await leaderboard_controllers.get_all(
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

