from datetime import datetime
from typing import Literal, Optional

from core.schemas import ObjectIdStr
from pydantic import BaseModel


class Histories(BaseModel):
    game_id: ObjectIdStr
    score: int
    winner: str
    duration: int
    created_at: datetime
    created_by: ObjectIdStr
