import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401
from app.core.error import ApiError
from app.database.base import Base
from app.models.registration import Registration
from app.schemas.registration import RegistrationCreate
from app.services.events import get_or_create_default_event
from app.services.exports import safe_spreadsheet_value
from app.services.registrations import create_registration


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:", future=True, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def payload(email="person@example.com", phone="9876543210"):
    return RegistrationCreate(
        full_name="Sample Person",
        phone_number=phone,
        additional_contact_number=None,
        email=email,
        educational_qualification="MBA",
        age=30,
        current_city="Chennai",
        gender="Male",
        alpha_alumni="Yes",
        profession="Technology Company",
        business_company_name="Sample Technologies",
        attendance="Will attend for sure",
        food_preference="Vegetarian",
        studied_standard="12th Standard",
        year_of_passing="2010",
        consent_given=True,
    )


def test_registration_persists_and_idempotency_returns_original(db):
    first = create_registration(db, payload(), "public_form", idempotency_key="same-key")
    second = create_registration(db, payload(), "public_form", idempotency_key="same-key")

    assert first.registration_id == second.registration_id
    assert first.registration_id.startswith("ABN-2026-")
    assert db.scalar(select(func.count(Registration.id))) == 1


def test_duplicate_email_or_phone_is_rejected(db):
    create_registration(db, payload(), "public_form")

    with pytest.raises(ApiError) as duplicate_email:
        create_registration(db, payload(email="PERSON@example.com", phone="9123456789"), "public_form")
    assert duplicate_email.value.status_code == 409

    with pytest.raises(ApiError) as duplicate_phone:
        create_registration(db, payload(email="other@example.com", phone="+91 9876543210"), "public_form")
    assert duplicate_phone.value.status_code == 409


def test_capacity_creates_waitlist(db):
    event = get_or_create_default_event(db)
    event.capacity = 1
    db.add(event)
    db.commit()

    first = create_registration(db, payload(email="one@example.com", phone="9876543210"), "public_form")
    second = create_registration(db, payload(email="two@example.com", phone="9876543211"), "public_form")

    assert first.registration_status == "confirmed"
    assert second.registration_status == "waitlisted"


def test_csv_formula_values_are_escaped():
    assert safe_spreadsheet_value("=SUM(A1:A2)") == "'=SUM(A1:A2)"
    assert safe_spreadsheet_value("normal") == "normal"
