import math
import uuid
from datetime import datetime
from typing import Iterable

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.error import ApiError
from app.database.base import utcnow
from app.models.admin import AdminUser
from app.models.event import Event
from app.models.registration import Registration
from app.schemas.registration import (
    ManualRegistrationCreate,
    RegistrationCreate,
    RegistrationPublicResult,
    RegistrationUpdate,
    StatusUpdate,
)
from app.services.audit import log_audit
from app.services.email import retry_confirmation_email, send_confirmation_email
from app.services.events import get_or_create_default_event
from app.services.normalization import normalise_email, normalise_phone
from app.services.sheets import retry_sheet_sync, sync_registration_to_sheet

SEAT_HOLDING_STATUSES = {"confirmed", "attended", "no_show"}


def event_time_label(event: Event) -> str:
    return f"{event.start_time.strftime('%I:%M %p')} to {event.end_time.strftime('%I:%M %p')}"


def event_date_label(event: Event) -> str:
    return event.event_date.strftime("%d %B")


def success_message(registration: Registration, event: Event) -> str:
    if registration.registration_status == "waitlisted":
        return "Your registration has been added to the waiting list. The event team will contact you if a seat becomes available."
    return (
        f"Your registration has been confirmed. We look forward to seeing you on "
        f"{event_date_label(event)} from {event_time_label(event)} at {event.venue}."
    )


def public_result(registration: Registration) -> RegistrationPublicResult:
    event = registration.event
    return RegistrationPublicResult(
        registration_id=registration.registration_id,
        full_name=registration.full_name,
        registration_status=registration.registration_status,
        email_status=registration.email_status,
        google_sheet_sync_status=registration.google_sheet_sync_status,
        event_date=event_date_label(event),
        event_time=event_time_label(event),
        venue=event.venue,
        message=success_message(registration, event),
    )


def ensure_registration_open(event: Event) -> None:
    now = utcnow()
    if not event.registration_open:
        raise ApiError(400, "REGISTRATION_CLOSED", "Registration for this event is currently closed.")
    if event.registration_start_at and now < event.registration_start_at:
        raise ApiError(400, "REGISTRATION_CLOSED", "Registration for this event is currently closed.")
    if event.registration_end_at and now > event.registration_end_at:
        raise ApiError(400, "REGISTRATION_CLOSED", "Registration for this event is currently closed.")


def confirmed_count(db: Session, event_id: int) -> int:
    return int(
        db.scalar(
            select(func.count(Registration.id)).where(
                Registration.event_id == event_id,
                Registration.registration_status.in_(SEAT_HOLDING_STATUSES),
            )
        )
        or 0
    )


def available_seats(db: Session, event: Event) -> int | None:
    if event.capacity is None:
        return None
    return max(event.capacity - confirmed_count(db, event.id), 0)


def determine_status(db: Session, event: Event) -> str:
    seats = available_seats(db, event)
    if seats is None or seats > 0:
        return "confirmed"
    return "waitlisted"


def duplicate_exists(db: Session, event_id: int, email: str | None, phone: str, exclude_id: int | None = None) -> bool:
    conditions = [Registration.normalised_phone == phone]
    if email:
        conditions.append(Registration.normalised_email == email)
    stmt = select(Registration.id).where(Registration.event_id == event_id, or_(*conditions))
    if exclude_id is not None:
        stmt = stmt.where(Registration.id != exclude_id)
    return db.scalar(stmt) is not None


def get_registration(db: Session, registration_id: str) -> Registration:
    conditions = [Registration.registration_id == registration_id]
    if registration_id.isdigit():
        conditions.append(Registration.id == int(registration_id))
    registration = db.scalar(select(Registration).where(or_(*conditions)))
    if not registration:
        raise ApiError(404, "REGISTRATION_NOT_FOUND", "Registration was not found.")
    return registration


def create_registration(
    db: Session,
    payload: RegistrationCreate | ManualRegistrationCreate,
    source: str,
    idempotency_key: str | None = None,
    admin_user: AdminUser | None = None,
) -> Registration:
    event = get_or_create_default_event(db)
    idempotency_key = idempotency_key.strip() if idempotency_key else None

    if idempotency_key:
        existing = db.scalar(
            select(Registration).where(
                Registration.event_id == event.id,
                Registration.idempotency_key == idempotency_key,
            )
        )
        if existing:
            return existing

    if source == "public_form":
        ensure_registration_open(event)

    email = normalise_email(str(payload.email)) if payload.email else None
    phone = normalise_phone(payload.phone_number)
    additional_phone = normalise_phone(payload.additional_contact_number) if payload.additional_contact_number else None
    if duplicate_exists(db, event.id, email, phone):
        raise ApiError(
            409,
            "DUPLICATE_REGISTRATION",
            "A registration already exists with this email address or phone number.",
        )

    status = determine_status(db, event)
    registration = Registration(
        event_id=event.id,
        registration_id=f"TEMP-{uuid.uuid4().hex[:24]}",
        idempotency_key=idempotency_key,
        full_name=payload.full_name,
        age=payload.age,
        gender=payload.gender,
        educational_qualification=payload.educational_qualification,
        email=email,
        normalised_email=email,
        phone_number=payload.phone_number.strip(),
        normalised_phone=phone,
        additional_contact_number=payload.additional_contact_number,
        normalised_additional_phone=additional_phone,
        current_city=payload.current_city,
        alpha_alumni=payload.alpha_alumni,
        profession=payload.profession,
        business_company_name=payload.business_company_name,
        attendance=payload.attendance,
        food_preference=payload.food_preference,
        studied_standard=payload.studied_standard,
        year_of_passing=payload.year_of_passing,
        professional_category=payload.profession,
        industry=payload.business_company_name,
        consent_given=payload.consent_given,
        registration_status=status,
        source=source,
        email_status="pending",
        google_sheet_sync_status="disabled",
        admin_notes=getattr(payload, "admin_notes", None),
    )

    try:
        db.add(registration)
        db.flush()
        registration.registration_id = f"ABN-{event.event_date.year}-{registration.id:06d}"
        if admin_user:
            log_audit(
                db,
                admin_user,
                "registration_created",
                "registration",
                registration.registration_id,
                None,
                {"source": source, "status": status},
            )
        db.commit()
        db.refresh(registration)
    except IntegrityError:
        db.rollback()
        raise ApiError(
            409,
            "DUPLICATE_REGISTRATION",
            "A registration already exists with this email address or phone number.",
        )

    registration = send_confirmation_email(db, registration)
    registration = sync_registration_to_sheet(db, registration)
    return registration


def update_registration(
    db: Session,
    registration: Registration,
    payload: RegistrationUpdate,
    admin_user: AdminUser,
) -> Registration:
    data = payload.model_dump(exclude_unset=True)
    old_values = {key: getattr(registration, key) for key in data}

    if "email" in data:
        data["email"] = normalise_email(str(data["email"])) if data["email"] else None
        data["normalised_email"] = data["email"]
    if "phone_number" in data:
        data["normalised_phone"] = normalise_phone(data["phone_number"])
    if "additional_contact_number" in data:
        data["normalised_additional_phone"] = normalise_phone(data["additional_contact_number"]) if data["additional_contact_number"] else None
    if "profession" in data:
        data["professional_category"] = data["profession"]
    if "business_company_name" in data:
        data["industry"] = data["business_company_name"]
    email = data.get("normalised_email", registration.normalised_email)
    phone = data.get("normalised_phone", registration.normalised_phone)
    if ("normalised_email" in data or "normalised_phone" in data) and duplicate_exists(
        db, registration.event_id, email, phone, exclude_id=registration.id
    ):
        raise ApiError(
            409,
            "DUPLICATE_REGISTRATION",
            "A registration already exists with this email address or phone number.",
        )

    for key, value in data.items():
        setattr(registration, key, value)
    log_audit(
        db,
        admin_user,
        "registration_edited",
        "registration",
        registration.registration_id,
        old_values,
        data,
    )
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return registration


def update_status(db: Session, registration: Registration, payload: StatusUpdate, admin_user: AdminUser) -> Registration:
    old_status = registration.registration_status
    new_status = payload.registration_status
    if old_status == new_status and payload.admin_notes is None:
        return registration
    if new_status == "confirmed" and old_status not in SEAT_HOLDING_STATUSES:
        seats = available_seats(db, registration.event)
        if seats == 0:
            raise ApiError(400, "CAPACITY_FULL", "No confirmed seats are currently available.")
    registration.registration_status = new_status
    if new_status == "cancelled":
        registration.cancelled_at = utcnow()
    elif old_status == "cancelled":
        registration.cancelled_at = None
    if payload.admin_notes is not None:
        registration.admin_notes = payload.admin_notes
    log_audit(
        db,
        admin_user,
        "registration_status_changed",
        "registration",
        registration.registration_id,
        {"registration_status": old_status},
        {"registration_status": new_status, "admin_notes": payload.admin_notes},
    )
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return registration


def retry_email(db: Session, registration: Registration, admin_user: AdminUser) -> Registration:
    log_audit(db, admin_user, "email_resent", "registration", registration.registration_id)
    db.commit()
    return retry_confirmation_email(db, registration)


def retry_google_sheet(db: Session, registration: Registration, admin_user: AdminUser) -> Registration:
    log_audit(db, admin_user, "google_sheet_sync_retried", "registration", registration.registration_id)
    db.commit()
    return retry_sheet_sync(db, registration)


def registration_filters(
    event_id: int,
    search: str | None = None,
    registration_status: str | None = None,
    gender: str | None = None,
    alpha_alumni: str | None = None,
    profession: str | None = None,
    professional_category: str | None = None,
    email_status: str | None = None,
    google_sheet_sync_status: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> list:
    filters = [Registration.event_id == event_id]
    if search:
        term = f"%{search.strip().lower()}%"
        filters.append(
            or_(
                func.lower(Registration.full_name).like(term),
                func.lower(Registration.registration_id).like(term),
                func.lower(Registration.email).like(term),
                Registration.normalised_phone.like(f"%{search.strip()}%"),
                func.lower(Registration.current_city).like(term),
                func.lower(Registration.profession).like(term),
                func.lower(Registration.business_company_name).like(term),
            )
        )
    if registration_status:
        filters.append(Registration.registration_status == registration_status)
    if gender:
        filters.append(Registration.gender == gender)
    if alpha_alumni:
        filters.append(Registration.alpha_alumni == alpha_alumni)
    profession_filter = profession or professional_category
    if profession_filter:
        filters.append(Registration.profession == profession_filter)
    if email_status:
        filters.append(Registration.email_status == email_status)
    if google_sheet_sync_status:
        filters.append(Registration.google_sheet_sync_status == google_sheet_sync_status)
    if date_from:
        filters.append(Registration.created_at >= date_from)
    if date_to:
        filters.append(Registration.created_at <= date_to)
    return filters


def sorted_registration_stmt(filters: Iterable, sort: str = "newest") -> Select:
    stmt = select(Registration).where(and_(*filters))
    if sort == "oldest":
        return stmt.order_by(Registration.created_at.asc())
    if sort == "name":
        return stmt.order_by(Registration.full_name.asc())
    if sort == "registration_id":
        return stmt.order_by(Registration.registration_id.asc())
    if sort == "status":
        return stmt.order_by(Registration.registration_status.asc(), Registration.created_at.desc())
    return stmt.order_by(Registration.created_at.desc())


def list_registrations(
    db: Session,
    event: Event,
    page: int = 1,
    page_size: int = 25,
    sort: str = "newest",
    **filters_kwargs,
) -> tuple[list[Registration], int, int]:
    filters = registration_filters(event.id, **filters_kwargs)
    total = int(db.scalar(select(func.count(Registration.id)).where(and_(*filters))) or 0)
    page_size = min(max(page_size, 1), 100)
    page = max(page, 1)
    pages = max(math.ceil(total / page_size), 1)
    stmt = sorted_registration_stmt(filters, sort).offset((page - 1) * page_size).limit(page_size)
    return list(db.scalars(stmt)), total, pages


def import_rows(
    db: Session,
    rows: list[dict[str, str]],
    mapping: dict[str, str],
    admin_user: AdminUser,
    skip_duplicates: bool = True,
) -> dict:
    total = len(rows)
    imported = duplicates = invalid = failed = 0
    for row in rows:
        try:
            data = {target: row.get(source, "") for source, target in mapping.items()}
            payload = RegistrationCreate(**data)
            try:
                create_registration(db, payload, "csv_import", admin_user=admin_user)
                imported += 1
            except ApiError as exc:
                if exc.code == "DUPLICATE_REGISTRATION" and skip_duplicates:
                    duplicates += 1
                else:
                    failed += 1
        except Exception:
            invalid += 1
    return {
        "total_rows": total,
        "successfully_imported": imported,
        "duplicates_skipped": duplicates,
        "invalid_rows": invalid,
        "failed_rows": failed,
    }
