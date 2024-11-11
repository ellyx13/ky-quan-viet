from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field
from core.schemas import ObjectIdStr


class CreateRequest(BaseModel):
    game_id: ObjectIdStr
    player_id: ObjectIdStr
    move_number: int
    state: list


class Response(BaseModel):
    id: str = Field(alias="_id")
    game_id: str
    player_id: str
    move_number: int
    state: list
    created_at: datetime
    created_by: str


class ListResponse(BaseModel):
    total_items: int
    total_page: int
    records_per_page: int
    results: List[Response]

