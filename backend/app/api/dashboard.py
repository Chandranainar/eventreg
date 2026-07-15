from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import require_admin
from app.core.config import settings
from app.database.session import get_db
from app.models.admin import AdminUser
from app.models.registration import Registration
from app.schemas.dashboard import DashboardSummary, RegistrationTrend
from app.services.events import get_or_create_default_event
from app.services.registrations import available_seats

router = APIRouter(tags=["admin-dashboard"])


def _count(db: Session, *filters) -> int:
    return int(db.scalar(select(func.count(Registration.id)).where(*filters)) or 0)


@router.get("/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db), admin: AdminUser = Depends(require_admin)):
    event = get_or_create_default_event(db)
    tz = ZoneInfo(settings.event_timezone)
    today = datetime.now(tz).date()
    start = datetime.combine(today, time.min, tzinfo=tz).astimezone(timezone.utc)
    end = datetime.combine(today, time.max, tzinfo=tz).astimezone(timezone.utc)
    base = Registration.event_id == event.id
    return DashboardSummary(
        total_registrations=_count(db, base),
        confirmed_registrations=_count(db, base, Registration.registration_status == "confirmed"),
        waitlisted_registrations=_count(db, base, Registration.registration_status == "waitlisted"),
        cancelled_registrations=_count(db, base, Registration.registration_status == "cancelled"),
        registrations_received_today=_count(db, base, Registration.created_at >= start, Registration.created_at <= end),
        alpha_alumni_count=_count(db, base, Registration.alpha_alumni == "Yes"),
        vegetarian_count=_count(db, base, Registration.food_preference == "Vegetarian"),
        non_vegetarian_count=_count(db, base, Registration.food_preference == "Non-Vegetarian"),
        available_seats=available_seats(db, event),
        failed_email_count=_count(db, base, Registration.email_status == "failed"),
        failed_google_sheets_sync_count=_count(db, base, Registration.google_sheet_sync_status == "failed"),
    )


@router.get("/registration-trends", response_model=list[RegistrationTrend])
def registration_trends(db: Session = Depends(get_db), admin: AdminUser = Depends(require_admin)):
    event = get_or_create_default_event(db)
    rows = db.execute(
        select(func.date(Registration.created_at), func.count(Registration.id))
        .where(Registration.event_id == event.id)
        .group_by(func.date(Registration.created_at))
        .order_by(func.date(Registration.created_at))
    ).all()
    return [RegistrationTrend(date=str(day), count=int(count)) for day, count in rows]
