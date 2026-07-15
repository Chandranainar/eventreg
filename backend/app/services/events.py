from datetime import date, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.error import ApiError
from app.models.event import Event
from app.schemas.event import EventUpdate


DEFAULT_DESCRIPTION = (
    "Entrepreneurs and professionals meet hosted by Alpha Business Network and Alpha Group of Institutions."
)


def get_or_create_default_event(db: Session) -> Event:
    event = db.scalar(select(Event).where(Event.public_id == settings.public_event_id))
    if event:
        return event
    event = Event(
        public_id=settings.public_event_id,
        name="Entrepreneurs & Professionals Meet",
        organization_name="Alpha Business Network",
        description=DEFAULT_DESCRIPTION,
        event_date=date(2026, 8, 8),
        start_time=time(10, 0),
        end_time=time(16, 0),
        venue="Alpha School, No.16, 3rd Cross Street, West C.I.T. Nagar, Chennai, Tamil Nadu 600035",
        contact_email="contactteamabn@gmail.com",
        contact_phone="+91 81909 26999 / 98849 80350",
        capacity=200,
        registration_open=True,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def update_event(db: Session, event: Event, payload: EventUpdate) -> Event:
    data = payload.model_dump(exclude_unset=True)
    if "start_time" in data and "end_time" in data and data["start_time"] >= data["end_time"]:
        raise ApiError(400, "INVALID_EVENT_TIME", "Event end time must be after start time.")
    start_time = data.get("start_time", event.start_time)
    end_time = data.get("end_time", event.end_time)
    if start_time >= end_time:
        raise ApiError(400, "INVALID_EVENT_TIME", "Event end time must be after start time.")
    if data.get("registration_start_at") and data.get("registration_end_at"):
        if data["registration_start_at"] >= data["registration_end_at"]:
            raise ApiError(400, "INVALID_REGISTRATION_WINDOW", "Registration closing time must be after opening time.")
    for key, value in data.items():
        setattr(event, key, value)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
