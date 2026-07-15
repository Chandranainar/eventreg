import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload = {"sub": subject, "exp": expire, "typ": "admin_access"}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def verify_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        if payload.get("typ") != "admin_access":
            return None
        return payload.get("sub")
    except Exception:
        return None


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def constant_time_equals(left: str | None, right: str | None) -> bool:
    if not left or not right:
        return False
    return secrets.compare_digest(left, right)
