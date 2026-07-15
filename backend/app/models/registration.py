from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database.base import Base, utcnow


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    registration_id = Column(String(32), unique=True, nullable=False, index=True)
    idempotency_key = Column(String(160), nullable=True)

    full_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(32), nullable=False)
    educational_qualification = Column(String(150), nullable=True)
    email = Column(String(254), nullable=True)
    normalised_email = Column(String(254), nullable=True)
    phone_number = Column(String(40), nullable=False)
    normalised_phone = Column(String(10), nullable=False)
    additional_contact_number = Column(String(40), nullable=True)
    normalised_additional_phone = Column(String(10), nullable=True)
    current_city = Column(String(120), nullable=False)
    alpha_alumni = Column(String(8), nullable=False)
    profession = Column(String(120), nullable=False)
    business_company_name = Column(String(150), nullable=False)
    attendance = Column(String(80), nullable=False)
    food_preference = Column(String(32), nullable=False)
    studied_standard = Column(String(80), nullable=True)
    year_of_passing = Column(String(20), nullable=True)
    professional_category = Column(String(120), nullable=False)
    industry = Column(String(150), nullable=False)
    consent_given = Column(Boolean, nullable=False)

    registration_status = Column(String(32), default="confirmed", nullable=False, index=True)
    source = Column(String(32), default="public_form", nullable=False, index=True)

    email_status = Column(String(16), default="pending", nullable=False, index=True)
    email_sent_at = Column(DateTime(timezone=True), nullable=True)
    email_failure_reason = Column(Text, nullable=True)
    email_retry_count = Column(Integer, default=0, nullable=False)

    google_sheet_sync_status = Column(String(16), default="disabled", nullable=False, index=True)
    google_sheet_synced_at = Column(DateTime(timezone=True), nullable=True)
    google_sheet_failure_reason = Column(Text, nullable=True)
    google_sheet_retry_count = Column(Integer, default=0, nullable=False)

    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    event = relationship("Event", back_populates="registrations")

    __table_args__ = (
        UniqueConstraint("event_id", "normalised_email", name="uq_registration_event_email"),
        UniqueConstraint("event_id", "normalised_phone", name="uq_registration_event_phone"),
        UniqueConstraint("event_id", "idempotency_key", name="uq_registration_event_idempotency_key"),
        Index("ix_registrations_search_name", "full_name"),
        Index("ix_registrations_created_status", "created_at", "registration_status"),
    )
