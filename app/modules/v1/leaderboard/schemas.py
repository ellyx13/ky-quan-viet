from fastapi import Query, Request
from datetime import datetime
from typing import List, Literal, Optional

from core.schemas import ObjectIdStr
from pydantic import BaseModel, Field
from utils.value import OrderBy


class PaginationParams:
    def __init__(
        self,
        request: Request,
        search: str = Query(None, description="Anything you want"),
        page: int = Query(default=1, gt=0),
        limit: int = Query(default=20, gt=0),
        fields: str = None,
        sort_by: str = Query("score", description="Anything you want"),
        order_by: OrderBy = Query(OrderBy.DECREASE.value, description="desc: Descending | asc: Ascending"),
    ):
        self.query = dict(request.query_params)
        self.search = search
        self.page = page
        self.limit = limit
        self.fields = fields
        self.sort_by = sort_by
        self.order_by = order_by.value
        


class Response(BaseModel):
    id: str = Field(alias="_id")
    fullname: str
    score: Optional[int] = None
    total_win: Optional[int] = None
    total_lose: Optional[int] = None
 


class ListResponse(BaseModel):
    total_items: int
    total_page: int
    records_per_page: int
    results: List[Response]

