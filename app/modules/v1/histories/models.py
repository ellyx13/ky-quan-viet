from datetime import datetime
from typing import Literal, Optional

from core.schemas import ObjectIdStr
from pydantic import BaseModel


class Histories(BaseModel):
    game_id: ObjectIdStr
    score: int
    winner: ObjectIdStr
    duration: int
    created_at: datetime
    created_by: ObjectIdStr
    updated_at: Optional[datetime] = None
    updated_by: Optional[ObjectIdStr] = None
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[ObjectIdStr] = None
