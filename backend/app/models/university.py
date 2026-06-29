"""University = the SaaS tenant. Each row is one Telangana university."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class University(Base):
    __tablename__ = "universities"

    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, unique=True, nullable=False, index=True)  # short code, e.g. "OU"
    name = Column(String, nullable=False)
    short_code = Column(String, nullable=False)
    university_type = Column(String, nullable=False)  # State / Central / Deemed / Private
    city = Column(String, nullable=False)
    state = Column(String, nullable=False, default="Telangana")
    established_year = Column(Integer, nullable=True)
    portal_url = Column(String, nullable=True)
    ai_enabled = Column(Boolean, nullable=False, default=False)
    status = Column(String, nullable=False, default="active")  # active / suspended
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
