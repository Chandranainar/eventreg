from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import require_admin
from app.database.session import get_db
from app.models.admin import AdminAuditLog, AdminUser
from app.schemas.audit import AuditLogRead

router = APIRouter(tags=["admin-audit"])


@router.get("/audit-logs", response_model=list[AuditLogRead])
def audit_logs(
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    return list(db.scalars(select(AdminAuditLog).order_by(AdminAuditLog.created_at.desc()).limit(limit)))
