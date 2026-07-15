from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import require_admin
from app.database.session import get_db
from app.models.admin import AdminUser
from app.schemas.event import EventAdmin, EventUpdate
from app.services.audit import log_audit
from app.services.events import get_or_create_default_event, update_event

router = APIRouter(tags=["admin-event"])


@router.get("/event", response_model=EventAdmin)
def get_event(db: Session = Depends(get_db), admin: AdminUser = Depends(require_admin)):
    return get_or_create_default_event(db)


@router.patch("/event", response_model=EventAdmin)
def patch_event(payload: EventUpdate, db: Session = Depends(get_db), admin: AdminUser = Depends(require_admin)):
    event = get_or_create_default_event(db)
    changed_keys = payload.model_dump(exclude_unset=True).keys()
    old_values = {key: getattr(event, key) for key in changed_keys}
    updated = update_event(db, event, payload)
    log_audit(db, admin, "event_settings_changed", "event", updated.public_id, old_values, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(updated)
    return updated
