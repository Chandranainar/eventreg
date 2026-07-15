from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.error import ApiError
from app.core.rate_limit import registration_limiter
from app.database.session import get_db
from app.schemas.event import EventPublic
from app.schemas.registration import RegistrationCreate, RegistrationPublicResult
from app.services.events import get_or_create_default_event
from app.services.registrations import create_registration, public_result

router = APIRouter(tags=["public"])


@router.get("/event", response_model=EventPublic)
def get_public_event(db: Session = Depends(get_db)):
    return get_or_create_default_event(db)


@router.post("/registrations", response_model=RegistrationPublicResult, status_code=201)
def submit_registration(
    payload: RegistrationCreate,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
):
    client = request.client.host if request.client else "unknown"
    if not registration_limiter.allow(client, settings.rate_limit_registration, settings.rate_limit_window_seconds):
        raise ApiError(429, "RATE_LIMITED", "Too many registration attempts. Please try again shortly.")
    registration = create_registration(db, payload, source="public_form", idempotency_key=idempotency_key)
    return public_result(registration)
