from datetime import datetime
from typing import Literal, Optional

from core.schemas import EmailStr, ObjectIdStr, PhoneStr
from pydantic import BaseModel


class Users(BaseModel):
    fullname: str
    email: EmailStr
    phone: Optional[PhoneStr] = None
    password: bytes
    type: Literal["admin", "user"]
    score: Optional[int] = None
    created_at: datetime
    created_by: ObjectIdStr
    updated_at: Optional[datetime] = None
    updated_by: Optional[ObjectIdStr] = None
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[ObjectIdStr] = None
