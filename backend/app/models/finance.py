"""
Finance & operations (Admin module):
Invoice, Payment, PayrollRun, Payslip, HallTicket, Expense.

Payments are stored generically; a real gateway (Stripe/Razorpay/PayPal) plugs
in later behind the service layer without changing these tables.
"""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
)

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, nullable=False, index=True)
    student_id = Column(String, ForeignKey("student_profiles.id"), nullable=False)
    description = Column(String, nullable=False)   # e.g. "Tuition Fee 2025-26"
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="INR")
    status = Column(String, nullable=False, default="unpaid")  # unpaid / paid / partial / overdue
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, nullable=False, index=True)
    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=False)
    amount = Column(Float, nullable=False)
    method = Column(String, nullable=False)   # UPI / Card / NetBanking / Cash
    provider_ref = Column(String, nullable=True)
    status = Column(String, nullable=False, default="success")  # success / failed / pending
    paid_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)


class PayrollRun(Base):
    __tablename__ = "payroll_runs"

    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, nullable=False, index=True)
    period = Column(String, nullable=False)   # e.g. "2026-05"
    status = Column(String, nullable=False, default="completed")  # draft / completed
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)


class Payslip(Base):
    __tablename__ = "payslips"

    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, nullable=False, index=True)
    payroll_run_id = Column(String, ForeignKey("payroll_runs.id"), nullable=False)
    professor_id = Column(String, ForeignKey("professor_profiles.id"), nullable=False)
    gross = Column(Float, nullable=False)
    deductions = Column(Float, nullable=False, default=0.0)
    net = Column(Float, nullable=False)


class HallTicket(Base):
    __tablename__ = "hall_tickets"

    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, nullable=False, index=True)
    student_id = Column(String, ForeignKey("student_profiles.id"), nullable=False)
    exam_name = Column(String, nullable=False)   # e.g. "Sem-1 End Exams 2025-26"
    eligibility = Column(String, nullable=False, default="eligible")  # eligible / blocked
    block_reason = Column(Text, nullable=True)   # e.g. low attendance / fee due
    issued_at = Column(DateTime(timezone=True), nullable=True)


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False)   # Infrastructure / Salaries / Utilities / Events / Library
    description = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    vendor = Column(String, nullable=True)
    spent_on = Column(Date, nullable=False)
