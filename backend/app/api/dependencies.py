from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import constant_time_equals, verify_access_token
from app.database.session import get_db
from app.models.admin import AdminUser

UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def require_admin(request: Request, db: Session = Depends(get_db)) -> AdminUser:
    token = request.cookies.get(settings.admin_cookie_name)
    subject = verify_access_token(token) if token else None
    if not subject:
        raise HTTPException(status_code=401)
    user = db.get(AdminUser, int(subject)) if subject.isdigit() else None
    if not user or not user.is_active:
        raise HTTPException(status_code=401)
    if request.method in UNSAFE_METHODS:
        csrf_cookie = request.cookies.get(settings.csrf_cookie_name)
        csrf_header = request.headers.get(settings.csrf_header_name)
        if not constant_time_equals(csrf_cookie, csrf_header):
            raise HTTPException(status_code=403, detail={"code": "CSRF_FAILED", "message": "Security token is missing or expired."})
    return user
