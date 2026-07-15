from sqlalchemy.orm import Session

from app.models.admin import AdminAuditLog, AdminUser


def log_audit(
    db: Session,
    admin_user: AdminUser | None,
    action: str,
    entity_type: str,
    entity_id: str | int,
    old_values: dict | None = None,
    new_values: dict | None = None,
) -> None:
    log = AdminAuditLog(
        admin_user_id=admin_user.id if admin_user else None,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        old_values=old_values,
        new_values=new_values,
    )
    db.add(log)
