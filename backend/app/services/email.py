import smtplib
from email.message import EmailMessage

from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.base import utcnow
from app.models.event import Event
from app.models.registration import Registration


def _event_time(event: Event) -> str:
    return f"{event.start_time.strftime('%I:%M %p')} to {event.end_time.strftime('%I:%M %p')}"


def _build_message(registration: Registration, event: Event) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = f"{event.name} - {registration.registration_status.title()}"
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = registration.email
    if registration.registration_status == "waitlisted":
        body = (
            f"Dear {registration.full_name},\n\n"
            f"Your registration for {event.name} has been added to the waiting list.\n"
            "The event team will contact you if a seat becomes available.\n\n"
            f"Registration ID: {registration.registration_id}\n"
            f"Date: {event.event_date.strftime('%d %B %Y')}\n"
            f"Time: {_event_time(event)}\n"
            f"Venue: {event.venue}\n"
        )
    else:
        body = (
            f"Dear {registration.full_name},\n\n"
            f"Your registration for {event.name} has been confirmed.\n\n"
            f"Registration ID: {registration.registration_id}\n"
            f"Date: {event.event_date.strftime('%d %B %Y')}\n"
            f"Time: {_event_time(event)}\n"
            f"Venue: {event.venue}\n"
        )
    if event.contact_email or event.contact_phone:
        body += f"\nEvent team contact: {event.contact_email or event.contact_phone}\n"
    msg.set_content(body)
    return msg


def send_confirmation_email(db: Session, registration: Registration) -> Registration:
    event = registration.event
    registration.email_status = "pending"
    registration.email_failure_reason = None
    if not registration.email:
        registration.email_status = "failed"
        registration.email_failure_reason = "No email address was provided."
        db.add(registration)
        db.commit()
        db.refresh(registration)
        return registration
    if not settings.smtp_host or not settings.smtp_from_email:
        registration.email_status = "failed"
        registration.email_failure_reason = "SMTP configuration is not complete."
        db.add(registration)
        db.commit()
        db.refresh(registration)
        return registration
    try:
        msg = _build_message(registration, event)
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
            smtp.starttls()
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(msg)
        registration.email_status = "sent"
        registration.email_sent_at = utcnow()
        registration.email_failure_reason = None
    except Exception as exc:
        registration.email_status = "failed"
        registration.email_failure_reason = str(exc)[:500]
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return registration


def retry_confirmation_email(db: Session, registration: Registration) -> Registration:
    registration.email_retry_count += 1
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return send_confirmation_email(db, registration)
