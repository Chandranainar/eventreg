import uuid

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text, Time
from sqlalchemy.orm import relationship

from app.database.base import Base, utcnow


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    organization_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    event_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    venue = Column(String(255), nullable=False)
    contact_email = Column(String(254), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    capacity = Column(Integer, nullable=True)
    registration_open = Column(Boolean, default=True, nullable=False)
    registration_start_at = Column(DateTime(timezone=True), nullable=True)
    registration_end_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    registrations = relationship("Registration", back_populates="event")
