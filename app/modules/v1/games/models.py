from datetime import datetime
from typing import Literal, Optional

from core.schemas import ObjectIdStr
from pydantic import BaseModel


class Games(BaseModel):
    code: int
    host_id: ObjectIdStr
    guest_id: Optional[ObjectIdStr] = None
    status: Literal["waiting", "in_progress", "completed"]
    type: Literal["public", "private"]
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    created_at: datetime
    created_by: ObjectIdStr
    updated_at: Optional[datetime] = None
    updated_by: Optional[ObjectIdStr] = None
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[ObjectIdStr] = None