"""Import all models so Base.metadata is fully populated."""

from app.models.university import University  # noqa: F401
from app.models.user import (  # noqa: F401
    User,
    StudentProfile,
    ProfessorProfile,
    AdminProfile,
)
from app.models.academics import (  # noqa: F401
    Department,
    Program,
    Course,
    Section,
    Enrollment,
    AttendanceRecord,
    Assessment,
    Mark,
)
from app.models.finance import (  # noqa: F401
    Invoice,
    Payment,
    PayrollRun,
    Payslip,
    HallTicket,
    Expense,
)
from app.models.audit import AuditLog, log_event, EventType  # noqa: F401
