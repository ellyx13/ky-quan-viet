from datetime import datetime
from typing import Literal, Optional

from core.schemas import ObjectIdStr
from pydantic import BaseModel




class Moves(BaseModel):
    game_id: ObjectIdStr
    player_id: ObjectIdStr
    move_number: int
    state: list
    created_at: datetime
    created_by: ObjectIdStr
    updated_at: Optional[datetime] = None
    updated_by: Optional[ObjectIdStr] = None
