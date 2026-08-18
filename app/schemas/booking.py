import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class BookingExtraction(BaseModel):
    is_booking_request: bool
    name: str | None = None
    email: str | None = None
    date: str | None = None
    time: str | None = None
    missing_fields: list[str] = []


class BookingCreate(BaseModel):
    name: str
    email: EmailStr
    date: str
    time: str


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: str
    interview_date: str
    interview_time: str
    created_at: datetime