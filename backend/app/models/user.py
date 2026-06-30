"""
Users and role-specific profiles.

`User` holds shared identity + auth fields and a `role` discriminator.
Each role has a profile table with its own attributes:
    student  -> StudentProfile
    professor-> ProfessorProfile
    admin    -> AdminProfile
"""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)  # student / professor / admin
    gender = Column(String, nullable=True)  # Male / Female
    phone = Column(String, nullable=True)
    auth_type = Column(String, nullable=False, default="local")  # local / sso
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    password_hash = Column(String, nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    roll_no = Column(String, nullable=False, unique=True, index=True)  # e.g. OU22CS001
    department_id = Column(String, ForeignKey("departments.id"), nullable=False)
    program_id = Column(String, ForeignKey("programs.id"), nullable=False)
    batch_year = Column(Integer, nullable=False)        # admission year
    current_year = Column(Integer, nullable=False)      # 1..4
    current_semester = Column(Integer, nullable=False)  # 1..8
    cgpa = Column(Float, nullable=True)
    date_of_birth = Column(Date, nullable=True)


class ProfessorProfile(Base):
    __tablename__ = "professor_profiles"

    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    employee_id = Column(String, nullable=False, unique=True, index=True)  # e.g. OU-FAC-1042
    department_id = Column(String, ForeignKey("departments.id"), nullable=False)
    designation = Column(String, nullable=False)   # Assistant/Associate/Professor/HOD
    specialization = Column(String, nullable=True)
    date_of_joining = Column(Date, nullable=True)
    monthly_salary = Column(Float, nullable=True)


class AdminProfile(Base):
    __tablename__ = "admin_profiles"

    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    employee_id = Column(String, nullable=False, unique=True, index=True)  # e.g. OU-ADM-007
    designation = Column(String, nullable=False)  # Registrar / Accounts Officer / Exam Controller
    office = Column(String, nullable=False)        # Administration / Accounts / Examinations
    date_of_joining = Column(Date, nullable=True)
