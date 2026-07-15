import csv
from datetime import date, datetime, time, timezone
from io import StringIO

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.dependencies import require_admin
from app.core.config import settings
from app.core.error import ApiError
from app.database.session import get_db
from app.models.admin import AdminUser
from app.schemas.registration import (
    ImportConfirmResponse,
    ImportPreviewRequest,
    ManualRegistrationCreate,
    PaginatedRegistrations,
    RegistrationListItem,
    RegistrationRead,
    RegistrationUpdate,
    StatusUpdate,
)
from app.services.events import get_or_create_default_event
from app.services.exports import registrations_to_csv, registrations_to_xlsx
from app.services.registrations import (
    create_registration,
    get_registration,
    import_rows,
    list_registrations,
    registration_filters,
    retry_email,
    retry_google_sheet,
    sorted_registration_stmt,
    update_registration,
    update_status,
)

router = APIRouter(tags=["admin-registrations"])


def _date_start(value: date | None):
    return datetime.combine(value, time.min, tzinfo=timezone.utc) if value else None


def _date_end(value: date | None):
    return datetime.combine(value, time.max, tzinfo=timezone.utc) if value else None


def _list_kwargs(
    search: str | None = None,
    registration_status: str | None = None,
    gender: str | None = None,
    alpha_alumni: str | None = None,
    profession: str | None = None,
    professional_category: str | None = None,
    email_status: str | None = None,
    google_sheet_sync_status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
):
    return {
        "search": search,
        "registration_status": registration_status,
        "gender": gender,
        "alpha_alumni": alpha_alumni,
        "profession": profession,
        "professional_category": professional_category,
        "email_status": email_status,
        "google_sheet_sync_status": google_sheet_sync_status,
        "date_from": _date_start(date_from),
        "date_to": _date_end(date_to),
    }


def _to_list_item(registration, serial_number: int) -> RegistrationListItem:
    return RegistrationListItem(
        serial_number=serial_number,
        id=registration.id,
        created_at=registration.created_at,
        registration_id=registration.registration_id,
        full_name=registration.full_name,
        phone_number=registration.normalised_phone,
        additional_contact_number=registration.normalised_additional_phone,
        email=registration.email,
        educational_qualification=registration.educational_qualification,
        age=registration.age,
        current_city=registration.current_city,
        gender=registration.gender,
        profession=registration.profession,
        business_company_name=registration.business_company_name,
        attendance=registration.attendance,
        food_preference=registration.food_preference,
        alpha_alumni=registration.alpha_alumni,
        studied_standard=registration.studied_standard,
        year_of_passing=registration.year_of_passing,
        registration_status=registration.registration_status,
        email_status=registration.email_status,
        google_sheet_sync_status=registration.google_sheet_sync_status,
    )


@router.get("/registrations/export/csv")
def export_csv(
    search: str | None = None,
    registration_status: str | None = None,
    gender: str | None = None,
    alpha_alumni: str | None = None,
    profession: str | None = None,
    professional_category: str | None = None,
    email_status: str | None = None,
    google_sheet_sync_status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    sort: str = "newest",
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    event = get_or_create_default_event(db)
    filters = registration_filters(
        event.id,
        **_list_kwargs(
            search=search,
            registration_status=registration_status,
            gender=gender,
            alpha_alumni=alpha_alumni,
            profession=profession,
            professional_category=professional_category,
            email_status=email_status,
            google_sheet_sync_status=google_sheet_sync_status,
            date_from=date_from,
            date_to=date_to,
        ),
    )
    registrations = list(db.scalars(sorted_registration_stmt(filters, sort)))
    content = registrations_to_csv(registrations)
    return Response(
        content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="abn-registrations.csv"'},
    )


@router.get("/registrations/export/xlsx")
def export_xlsx(
    search: str | None = None,
    registration_status: str | None = None,
    gender: str | None = None,
    alpha_alumni: str | None = None,
    profession: str | None = None,
    professional_category: str | None = None,
    email_status: str | None = None,
    google_sheet_sync_status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    sort: str = "newest",
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    event = get_or_create_default_event(db)
    filters = registration_filters(
        event.id,
        **_list_kwargs(
            search=search,
            registration_status=registration_status,
            gender=gender,
            alpha_alumni=alpha_alumni,
            profession=profession,
            professional_category=professional_category,
            email_status=email_status,
            google_sheet_sync_status=google_sheet_sync_status,
            date_from=date_from,
            date_to=date_to,
        ),
    )
    registrations = list(db.scalars(sorted_registration_stmt(filters, sort)))
    content = registrations_to_xlsx(registrations)
    return Response(
        content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="abn-registrations.xlsx"'},
    )


@router.post("/registrations/import/preview")
async def import_preview(file: UploadFile = File(...), admin: AdminUser = Depends(require_admin)):
    content = await file.read(settings.max_upload_bytes + 1)
    if len(content) > settings.max_upload_bytes:
        raise ApiError(400, "UPLOAD_TOO_LARGE", "CSV file is too large.")
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(StringIO(text))
    rows = list(reader)
    return {
        "success": True,
        "columns": reader.fieldnames or [],
        "total_rows": len(rows),
        "sample_rows": rows[:10],
        "rows": rows,
    }


@router.post("/registrations/import/confirm", response_model=ImportConfirmResponse)
def import_confirm(
    payload: ImportPreviewRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    return import_rows(db, payload.rows, payload.mapping, admin, payload.skip_duplicates)


@router.get("/registrations", response_model=PaginatedRegistrations)
def registrations(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: str | None = None,
    registration_status: str | None = None,
    gender: str | None = None,
    alpha_alumni: str | None = None,
    profession: str | None = None,
    professional_category: str | None = None,
    email_status: str | None = None,
    google_sheet_sync_status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    sort: str = "newest",
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    event = get_or_create_default_event(db)
    records, total, pages = list_registrations(
        db,
        event,
        page,
        page_size,
        sort,
        **_list_kwargs(
            search=search,
            registration_status=registration_status,
            gender=gender,
            alpha_alumni=alpha_alumni,
            profession=profession,
            professional_category=professional_category,
            email_status=email_status,
            google_sheet_sync_status=google_sheet_sync_status,
            date_from=date_from,
            date_to=date_to,
        ),
    )
    start = (page - 1) * page_size + 1
    items = [_to_list_item(registration, start + index) for index, registration in enumerate(records)]
    return PaginatedRegistrations(items=items, total=total, page=page, page_size=page_size, pages=pages)


@router.post("/registrations", response_model=RegistrationRead, status_code=201)
def manual_registration(
    payload: ManualRegistrationCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    return create_registration(db, payload, source="admin_manual", admin_user=admin)


@router.get("/registrations/{registration_id}", response_model=RegistrationRead)
def registration_detail(
    registration_id: str,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    return get_registration(db, registration_id)


@router.patch("/registrations/{registration_id}", response_model=RegistrationRead)
def edit_registration(
    registration_id: str,
    payload: RegistrationUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    return update_registration(db, get_registration(db, registration_id), payload, admin)


@router.patch("/registrations/{registration_id}/status", response_model=RegistrationRead)
def change_status(
    registration_id: str,
    payload: StatusUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    return update_status(db, get_registration(db, registration_id), payload, admin)


@router.post("/registrations/{registration_id}/retry-email", response_model=RegistrationRead)
def resend_email(
    registration_id: str,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    return retry_email(db, get_registration(db, registration_id), admin)


@router.post("/registrations/{registration_id}/retry-sheet-sync", response_model=RegistrationRead)
def retry_sheet(
    registration_id: str,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    return retry_google_sheet(db, get_registration(db, registration_id), admin)
