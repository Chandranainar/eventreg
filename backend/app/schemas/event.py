from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class EventBase(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    organization_name: str = Field(min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    event_date: date
    start_time: time
    end_time: time
    venue: str = Field(min_length=2, max_length=255)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(default=None, max_length=50)
    capacity: int | None = Field(default=None, ge=1)
    registration_open: bool = True
    registration_start_at: datetime | None = None
    registration_end_at: datetime | None = None

    @field_validator("name", "organization_name", "description", "venue", "contact_phone", mode="before")
    @classmethod
    def trim_strings(cls, value):
        return value.strip() if isinstance(value, str) else value


class EventPublic(EventBase):
    public_id: str

    model_config = ConfigDict(from_attributes=True)


class EventAdmin(EventPublic):
    id: int
    created_at: datetime
    updated_at: datetime


class EventUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    organization_name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    event_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    venue: str | None = Field(default=None, min_length=2, max_length=255)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(default=None, max_length=50)
    capacity: int | None = Field(default=None, ge=1)
    registration_open: bool | None = None
    registration_start_at: datetime | None = None
    registration_end_at: datetime | None = None

    @field_validator("name", "organization_name", "description", "venue", "contact_phone", mode="before")
    @classmethod
    def trim_strings(cls, value):
        return value.strip() if isinstance(value, str) else value
