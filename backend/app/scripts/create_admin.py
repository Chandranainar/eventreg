import getpass

from sqlalchemy import select

import app.models  # noqa: F401
from app.core.security import hash_password
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.models.admin import AdminUser


def prompt_non_empty(label: str) -> str:
    while True:
        value = input(label).strip()
        if value:
            return value
        print("This field is required.")


def main() -> None:
    Base.metadata.create_all(bind=engine)
    name = prompt_non_empty("Admin name: ")
    email = prompt_non_empty("Admin email: ").lower()
    while True:
        password = getpass.getpass("Password: ")
        confirmation = getpass.getpass("Confirm password: ")
        if password != confirmation:
            print("Passwords do not match.")
            continue
        if len(password) < 12:
            print("Use at least 12 characters.")
            continue
        break

    db = SessionLocal()
    try:
        existing = db.scalar(select(AdminUser).where(AdminUser.email == email))
        if existing:
            raise SystemExit("An admin with this email already exists.")
        admin = AdminUser(name=name, email=email, password_hash=hash_password(password), is_active=True)
        db.add(admin)
        db.commit()
        print(f"Created admin: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
