"""
Academic structure & records:
Department -> Program -> Course -> Section -> Enrollment
plus AttendanceRecord, Assessment, Mark.
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


class Department(Base):
    __tablename__ = "departments"

    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)  # CSE, ECE, MEC ...


class Program(Base):
    __tablename__ = "programs"

    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, nullable=False, index=True)
    department_id = Column(String, ForeignKey("departments.id"), nullable=False)
    name = Column(String, nullable=False)        # e.g. "B.Tech Computer Science"
    degree = Column(String, nullable=False)      # B.Tech / M.Tech / MBA / B.Sc ...
    duration_years = Column(Integer, nullable=False)


class Course(Base):
    __tablename__ = "courses"

    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, nullable=False, index=True)
    department_id = Column(String, ForeignKey("departments.id"), nullable=False)
    professor_id = Column(String, ForeignKey("professor_profiles.id"), nullable=True)
    code = Column(String, nullable=False)        # e.g. CS301
    title = Column(String, nullable=False)
    credits = Column(Integer, nullable=False, default=3)
    semester = Column(Integer, nullable=False)


class Section(Base):
    __tablename__ = "sections"

    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, nullable=False, index=True)
    course_id = Column(String, ForeignKey("courses.id"), nullable=False)
    name = Column(String, nullable=False)            # A / B
    academic_year = Column(String, nullable=False)   # 2025-26
    term = Column(String, nullable=False)            # Sem-1 / Sem-2


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, nullable=False, index=True)
    section_id = Column(String, ForeignKey("sections.id"), nullable=False)
    student_id = Column(String, ForeignKey("student_profiles.id"), nullable=False)
    status = Column(String, nullable=False, default="enrolled")  # enrolled / dropped


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, nullable=False, index=True)
    section_id = Column(String, ForeignKey("sections.id"), nullable=False)
    student_id = Column(String, ForeignKey("student_profiles.id"), nullable=False)
    class_date = Column(Date, nullable=False)
    status = Column(String, nullable=False)  # present / absent / late


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, nullable=False, index=True)
    section_id = Column(String, ForeignKey("sections.id"), nullable=False)
    type = Column(String, nullable=False)        # Quiz / Mid-1 / Mid-2 / Assignment / Final
    max_marks = Column(Float, nullable=False)
    weightage = Column(Float, nullable=False)    # percentage weight in final grade
    held_on = Column(Date, nullable=True)


class Mark(Base):
    __tablename__ = "marks"

    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, nullable=False, index=True)
    assessment_id = Column(String, ForeignKey("assessments.id"), nullable=False)
    student_id = Column(String, ForeignKey("student_profiles.id"), nullable=False)
    score = Column(Float, nullable=False)
