from app.api.admin_registrations import router as admin_router
from app.api.audit import router as audit_router
from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.event import router as event_router
from app.api.public import router as public_router

__all__ = [
    "admin_router",
    "audit_router",
    "auth_router",
    "dashboard_router",
    "event_router",
    "public_router",
]
