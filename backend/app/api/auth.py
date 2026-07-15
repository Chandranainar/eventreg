from datetime import timedelta

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import require_admin
from app.core.config import settings
from app.core.error import ApiError
from app.core.rate_limit import login_limiter
from app.core.security import create_access_token, create_csrf_token, verify_password
from app.database.base import utcnow
from app.database.session import get_db
from app.models.admin import AdminUser
from app.schemas.auth import AdminUserRead, LoginRequest, LoginResponse

router = APIRouter(tags=["admin-auth"])


def _cookie_options() -> dict:
    options = {
        "secure": settings.cookie_secure,
        "samesite": "lax",
        "path": "/",
        "domain": settings.cookie_domain,
    }
    return {key: value for key, value in options.items() if value is not None}


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    client = request.client.host if request.client else "unknown"
    if not login_limiter.allow(f"{client}:{payload.email}", settings.rate_limit_login, settings.rate_limit_window_seconds):
        raise ApiError(429, "RATE_LIMITED", "Too many login attempts. Please try again shortly.")
    admin = db.scalar(select(AdminUser).where(AdminUser.email == str(payload.email).lower()))
    if not admin or not admin.is_active or not verify_password(payload.password, admin.password_hash):
        raise ApiError(401, "INVALID_LOGIN", "Invalid email or password.")

    admin.last_login_at = utcnow()
    db.add(admin)
    db.commit()
    db.refresh(admin)

    token = create_access_token(str(admin.id), timedelta(minutes=settings.access_token_expire_minutes))
    csrf_token = create_csrf_token()
    max_age = settings.access_token_expire_minutes * 60
    response.set_cookie(settings.admin_cookie_name, token, httponly=True, max_age=max_age, **_cookie_options())
    response.set_cookie(settings.csrf_cookie_name, csrf_token, httponly=False, max_age=max_age, **_cookie_options())
    user = AdminUserRead.model_validate(admin)
    user.csrf_token = csrf_token
    return LoginResponse(user=user)


@router.post("/logout")
def logout(response: Response, admin: AdminUser = Depends(require_admin)):
    response.delete_cookie(settings.admin_cookie_name, path="/", domain=settings.cookie_domain)
    response.delete_cookie(settings.csrf_cookie_name, path="/", domain=settings.cookie_domain)
    return {"success": True}


@router.get("/me", response_model=AdminUserRead)
def me(request: Request, admin: AdminUser = Depends(require_admin)):
    user = AdminUserRead.model_validate(admin)
    user.csrf_token = request.cookies.get(settings.csrf_cookie_name)
    return user
