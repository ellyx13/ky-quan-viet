from datetime import datetime
from typing import List, Literal, Optional

from core.schemas import ObjectIdStr
from pydantic import BaseModel, Field



class Response(BaseModel):
    id: str = Field(alias="_id")
    game_id: str
    score: int
    winner: str
    duration: int
    game_name: Optional[str] = None
    guest_name: Optional[str] = None
    is_host_win: Optional[bool] = None
    created_at: datetime
    created_by: str


class ListResponse(BaseModel):
    total_items: int
    total_page: int
    records_per_page: int
    results: List[Response]

