"""Tenant Admin (university admin) endpoints — scoped to the admin's own tenant_id."""

from fastapi import APIRouter, Depends
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.auth import require_role
from app.database import get_db
from app.models.academics import (
    AttendanceRecord,
    Course,
    Department,
)
from app.models.finance import (
    Expense,
    HallTicket,
    Invoice,
    Payment,
    PayrollRun,
    Payslip,
)
from app.models.university import University
from app.models.user import ProfessorProfile, StudentProfile, User

router = APIRouter(prefix="/tenant", tags=["tenant-admin"])
ADMIN = require_role("admin")


@router.get("/overview")
def overview(db: Session = Depends(get_db), user=Depends(ADMIN)):
    tid = user.tenant_id
    uni = db.query(University).filter(University.tenant_id == tid).first()
    collected = float(db.query(func.coalesce(func.sum(Payment.amount), 0))
                      .filter(Payment.tenant_id == tid, Payment.status == "success").scalar())
    pending = float(db.query(func.coalesce(func.sum(Invoice.amount), 0))
                    .filter(Invoice.tenant_id == tid, Invoice.status.in_(["unpaid", "overdue"])).scalar())
    expenses = float(db.query(func.coalesce(func.sum(Expense.amount), 0))
                     .filter(Expense.tenant_id == tid).scalar())
    payroll = float(db.query(func.coalesce(func.sum(Payslip.net), 0))
                    .filter(Payslip.tenant_id == tid).scalar())
    return {
        "university": {
            "name": uni.name if uni else tid,
            "city": uni.city if uni else "",
            "ai_enabled": uni.ai_enabled if uni else False,
            "status": uni.status if uni else "active",
        },
        "total_students": db.query(StudentProfile).filter(StudentProfile.tenant_id == tid).count(),
        "total_professors": db.query(ProfessorProfile).filter(ProfessorProfile.tenant_id == tid).count(),
        "total_departments": db.query(Department).filter(Department.tenant_id == tid).count(),
        "total_courses": db.query(Course).filter(Course.tenant_id == tid).count(),
        "fees_collected": collected,
        "fees_pending": pending,
        "total_expenses": expenses,
        "monthly_payroll": payroll,
    }


@router.get("/students")
def students(db: Session = Depends(get_db), user=Depends(ADMIN)):
    tid = user.tenant_id
    deptmap = dict(db.query(Department.id, Department.name).filter(Department.tenant_id == tid).all())
    att = db.query(
        AttendanceRecord.student_id,
        func.count(AttendanceRecord.id),
        func.sum(case((AttendanceRecord.status == "present", 1), else_=0)),
    ).filter(AttendanceRecord.tenant_id == tid).group_by(AttendanceRecord.student_id).all()
    attmap = {sid: round(present / total * 100, 1) for sid, total, present in att if total}
    invmap = dict(db.query(Invoice.student_id, Invoice.status).filter(Invoice.tenant_id == tid).all())
    htmap = dict(db.query(HallTicket.student_id, HallTicket.eligibility).filter(HallTicket.tenant_id == tid).all())
    rows = []
    for s, u in (db.query(StudentProfile, User)
                 .join(User, User.id == StudentProfile.user_id)
                 .filter(StudentProfile.tenant_id == tid).all()):
        rows.append({
            "roll_no": s.roll_no, "name": u.full_name, "email": u.email,
            "department": deptmap.get(s.department_id, "-"),
            "batch_year": s.batch_year, "current_year": s.current_year,
            "cgpa": s.cgpa, "attendance": attmap.get(s.id, 0.0),
            "fee_status": invmap.get(s.id, "-"),
            "hall_ticket": htmap.get(s.id, "-"),
        })
    rows.sort(key=lambda r: r["roll_no"])
    return rows


@router.get("/professors")
def professors(db: Session = Depends(get_db), user=Depends(ADMIN)):
    tid = user.tenant_id
    deptmap = dict(db.query(Department.id, Department.name).filter(Department.tenant_id == tid).all())
    netmap = dict(db.query(Payslip.professor_id, Payslip.net).filter(Payslip.tenant_id == tid).all())
    rows = []
    for p, u in (db.query(ProfessorProfile, User)
                 .join(User, User.id == ProfessorProfile.user_id)
                 .filter(ProfessorProfile.tenant_id == tid).all()):
        rows.append({
            "employee_id": p.employee_id, "name": u.full_name, "email": u.email,
            "designation": p.designation, "department": deptmap.get(p.department_id, "-"),
            "specialization": p.specialization, "salary": p.monthly_salary,
            "net_pay": float(netmap.get(p.id, 0) or 0),
        })
    rows.sort(key=lambda r: r["employee_id"])
    return rows


@router.get("/payments")
def payments(db: Session = Depends(get_db), user=Depends(ADMIN)):
    tid = user.tenant_id
    namemap = dict(db.query(StudentProfile.id, User.full_name)
                   .join(User, User.id == StudentProfile.user_id)
                   .filter(StudentProfile.tenant_id == tid).all())
    rollmap = dict(db.query(StudentProfile.id, StudentProfile.roll_no)
                   .filter(StudentProfile.tenant_id == tid).all())
    paid = dict(db.query(Payment.invoice_id, Payment.amount).filter(Payment.tenant_id == tid).all())
    method = dict(db.query(Payment.invoice_id, Payment.method).filter(Payment.tenant_id == tid).all())
    rows = []
    for inv in db.query(Invoice).filter(Invoice.tenant_id == tid).all():
        rows.append({
            "student": namemap.get(inv.student_id, "-"),
            "roll_no": rollmap.get(inv.student_id, "-"),
            "description": inv.description, "amount": inv.amount,
            "status": inv.status, "due_date": inv.due_date,
            "paid": float(paid.get(inv.id, 0) or 0),
            "method": method.get(inv.id, "-"),
        })
    rows.sort(key=lambda r: r["roll_no"])
    return rows


@router.get("/payroll")
def payroll(db: Session = Depends(get_db), user=Depends(ADMIN)):
    tid = user.tenant_id
    profmap = dict(db.query(ProfessorProfile.id, User.full_name)
                   .join(User, User.id == ProfessorProfile.user_id)
                   .filter(ProfessorProfile.tenant_id == tid).all())
    empmap = dict(db.query(ProfessorProfile.id, ProfessorProfile.employee_id)
                  .filter(ProfessorProfile.tenant_id == tid).all())
    runmap = dict(db.query(PayrollRun.id, PayrollRun.period).filter(PayrollRun.tenant_id == tid).all())
    rows = []
    for ps in db.query(Payslip).filter(Payslip.tenant_id == tid).all():
        rows.append({
            "employee_id": empmap.get(ps.professor_id, "-"),
            "name": profmap.get(ps.professor_id, "-"),
            "period": runmap.get(ps.payroll_run_id, "-"),
            "gross": ps.gross, "deductions": ps.deductions, "net": ps.net,
        })
    rows.sort(key=lambda r: r["employee_id"])
    return rows


@router.get("/hall-tickets")
def hall_tickets(db: Session = Depends(get_db), user=Depends(ADMIN)):
    tid = user.tenant_id
    namemap = dict(db.query(StudentProfile.id, User.full_name)
                   .join(User, User.id == StudentProfile.user_id)
                   .filter(StudentProfile.tenant_id == tid).all())
    rollmap = dict(db.query(StudentProfile.id, StudentProfile.roll_no)
                   .filter(StudentProfile.tenant_id == tid).all())
    rows = []
    for h in db.query(HallTicket).filter(HallTicket.tenant_id == tid).all():
        rows.append({
            "student": namemap.get(h.student_id, "-"),
            "roll_no": rollmap.get(h.student_id, "-"),
            "exam_name": h.exam_name, "eligibility": h.eligibility,
            "block_reason": h.block_reason, "issued_at": h.issued_at,
        })
    rows.sort(key=lambda r: r["roll_no"])
    return rows


@router.get("/expenses")
def expenses(db: Session = Depends(get_db), user=Depends(ADMIN)):
    tid = user.tenant_id
    rows = []
    for e in db.query(Expense).filter(Expense.tenant_id == tid).order_by(Expense.spent_on.desc()).all():
        rows.append({
            "category": e.category, "description": e.description,
            "amount": e.amount, "vendor": e.vendor, "spent_on": e.spent_on,
        })
    return rows
