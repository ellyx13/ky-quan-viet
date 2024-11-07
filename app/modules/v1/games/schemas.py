from datetime import datetime
from typing import List, Literal, Optional

from core.schemas import ObjectIdStr
from pydantic import BaseModel, Field


class CreateRequest(BaseModel):
    host_id: ObjectIdStr
    guest_id: Optional[ObjectIdStr] = None
    type: Literal["public", "private"]


class Response(BaseModel):
    id: str = Field(alias="_id")
    code: int
    host_id: str
    guest_id: Optional[str] = None
    status: str
    type: str
    start_at: Optional[str] = None
    end_at: Optional[str] = None
    created_at: datetime
    created_by: str


class ListResponse(BaseModel):
    total_items: int
    total_page: int
    records_per_page: int
    results: List[Response]


class EditRequest(BaseModel):
    type: Optional[Literal["public", "private"]] = None
