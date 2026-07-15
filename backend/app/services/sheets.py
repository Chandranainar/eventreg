from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.base import utcnow
from app.models.registration import Registration


def sync_registration_to_sheet(db: Session, registration: Registration) -> Registration:
    if not settings.google_sheets_sync_enabled:
        registration.google_sheet_sync_status = "disabled"
        db.add(registration)
        db.commit()
        db.refresh(registration)
        return registration

    registration.google_sheet_sync_status = "pending"
    registration.google_sheet_failure_reason = None
    try:
        if not settings.google_sheet_id or not settings.google_service_account_file:
            raise RuntimeError("Google Sheets configuration is not complete.")
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        credentials = service_account.Credentials.from_service_account_file(
            settings.google_service_account_file,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        service = build("sheets", "v4", credentials=credentials, cache_discovery=False)
        values = [[
            registration.created_at.isoformat(),
            registration.registration_id,
            registration.full_name,
            registration.normalised_phone,
            registration.normalised_additional_phone or "",
            registration.email or "",
            registration.educational_qualification or "",
            registration.age,
            registration.current_city,
            registration.gender,
            registration.profession,
            registration.business_company_name,
            registration.attendance,
            registration.food_preference,
            registration.alpha_alumni,
            registration.studied_standard or "",
            registration.year_of_passing or "",
            registration.registration_status,
        ]]
        service.spreadsheets().values().append(
            spreadsheetId=settings.google_sheet_id,
            range="A:R",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": values},
        ).execute()
        registration.google_sheet_sync_status = "synced"
        registration.google_sheet_synced_at = utcnow()
        registration.google_sheet_failure_reason = None
    except Exception as exc:
        registration.google_sheet_sync_status = "failed"
        registration.google_sheet_failure_reason = str(exc)[:500]
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return registration


def retry_sheet_sync(db: Session, registration: Registration) -> Registration:
    registration.google_sheet_retry_count += 1
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return sync_registration_to_sheet(db, registration)
