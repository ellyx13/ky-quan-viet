from datetime import datetime
from typing import List, Literal, Optional

from core.schemas import ObjectIdStr
from pydantic import BaseModel, Field


class CreateRequest(BaseModel):
    name: str
    is_guest_ai: Optional[bool] = False
    type: Literal["public", "private"]
    level: Optional[Literal["easy", "medium", "hard"]] = None


class Response(BaseModel):
    id: str = Field(alias="_id")
    name: str
    code: int
    host_id: str
    guest_id: Optional[str] = None
    is_guest_ai: Optional[bool] = None
    status: str
    type: str
    level: Optional[str] = None
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
    name: Optional[str] = None
    type: Optional[Literal["public", "private"]] = None
