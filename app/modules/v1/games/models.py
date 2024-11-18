from datetime import datetime
from typing import Literal, Optional

from core.schemas import ObjectIdStr
from pydantic import BaseModel


class Games(BaseModel):
    name: str
    code: int
    host_id: ObjectIdStr
    guest_id: Optional[ObjectIdStr] = None
    is_guest_ai: Optional[bool] = False
    status: Literal["pending", "waiting", "in_progress", "completed"]
    type: Literal["public", "private"]
    level: Optional[Literal["easy", "medium", "hard"]] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    created_at: datetime
    created_by: ObjectIdStr
    updated_at: Optional[datetime] = None
    updated_by: Optional[ObjectIdStr] = None
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[ObjectIdStr] = None