from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

import app.models  # noqa: F401
from app.api.routes import admin_router, audit_router, auth_router, dashboard_router, event_router, public_router
from app.core.config import settings
from app.core.error import (
    ApiError,
    api_error_handler,
    api_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.core.security import hash_password
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.models.admin import AdminUser
from app.services.events import get_or_create_default_event
from sqlalchemy import select

Base.metadata.create_all(bind=engine)

def ensure_sqlite_google_form_columns() -> None:
    if engine.dialect.name != "sqlite":
        return
    additions = {
        "additional_contact_number": "ALTER TABLE registrations ADD COLUMN additional_contact_number VARCHAR(40)",
        "normalised_additional_phone": "ALTER TABLE registrations ADD COLUMN normalised_additional_phone VARCHAR(10)",
        "current_city": "ALTER TABLE registrations ADD COLUMN current_city VARCHAR(120) NOT NULL DEFAULT 'Chennai'",
        "profession": "ALTER TABLE registrations ADD COLUMN profession VARCHAR(120) NOT NULL DEFAULT 'Technology Company'",
        "business_company_name": "ALTER TABLE registrations ADD COLUMN business_company_name VARCHAR(150) NOT NULL DEFAULT 'Not Provided'",
        "attendance": "ALTER TABLE registrations ADD COLUMN attendance VARCHAR(80) NOT NULL DEFAULT 'Will attend for sure'",
        "food_preference": "ALTER TABLE registrations ADD COLUMN food_preference VARCHAR(32) NOT NULL DEFAULT 'Vegetarian'",
        "studied_standard": "ALTER TABLE registrations ADD COLUMN studied_standard VARCHAR(80)",
        "year_of_passing": "ALTER TABLE registrations ADD COLUMN year_of_passing VARCHAR(20)",
    }
    with engine.begin() as connection:
        existing = {row[1] for row in connection.exec_driver_sql("PRAGMA table_info(registrations)").fetchall()}
        for column, statement in additions.items():
            if column not in existing:
                connection.exec_driver_sql(statement)


ensure_sqlite_google_form_columns()


app = FastAPI(
    title="ABN Event Registration API",
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if settings.is_production:
        response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'"
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, api_exception_handler)

try:
    from fastapi import HTTPException

    app.add_exception_handler(HTTPException, http_exception_handler)
except Exception:
    pass

app.include_router(public_router, prefix="/api/public")
app.include_router(auth_router, prefix="/api/admin/auth")
app.include_router(admin_router, prefix="/api/admin")
app.include_router(event_router, prefix="/api/admin")
app.include_router(dashboard_router, prefix="/api/admin/dashboard")
app.include_router(audit_router, prefix="/api/admin")


@app.on_event("startup")
def seed_initial_data():
    db = SessionLocal()
    try:
        get_or_create_default_event(db)
        if settings.bootstrap_admin_email and settings.bootstrap_admin_password:
            email = settings.bootstrap_admin_email.strip().lower()
            admin = db.scalar(select(AdminUser).where(AdminUser.email == email))
            if admin:
                admin.name = settings.bootstrap_admin_name or admin.name
                admin.password_hash = hash_password(settings.bootstrap_admin_password)
                admin.is_active = True
            else:
                admin = AdminUser(
                    name=settings.bootstrap_admin_name or "ABN Admin",
                    email=email,
                    password_hash=hash_password(settings.bootstrap_admin_password),
                    is_active=True,
                )
                db.add(admin)
            db.commit()
    finally:
        db.close()


@app.get("/api/health")
def health_check():
    return {"success": True, "status": "ok"}
