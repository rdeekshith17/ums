# UniAI — Multi-Tenant University AI Dashboard (PRD)

## Original Problem Statement
AI-powered web dashboard for universities with 3 roles — students (LLM+RAG on professor notes), professors (attendance/marks/performance analytics), administration (payments, payroll, hall tickets, expenses). Built as a multi-tenant SaaS for Telangana-state universities.

## Architecture
- **Frontend:** React SPA (role-based routing, JWT in localStorage, Tailwind, clean education/enterprise theme).
- **Backend:** FastAPI (`server.py`) + SQLAlchemy ORM, all routes under `/api`.
- **Database:** SQLAlchemy models designed for PostgreSQL; running on a persistent **SQLite** file (`sqlite:////app/backend/uniai_dev.db`) in this sandbox because apt-installed Postgres resets on sandbox restart. **Production target = PostgreSQL** (native dump at `/app/backend/backups/uniai_postgres.dump`).
- **Auth:** JWT email/password (bcrypt + PyJWT), `require_role` guards, tenant_id carried in token.

## Data Model (17 tables)
universities, users, student_profiles, professor_profiles, admin_profiles, departments, programs, courses, sections, enrollments, attendance_records, assessments, marks, invoices, payments, payroll_runs, payslips, hall_tickets, expenses, audit_logs.

## Seeded Data
8 real Telangana universities (OU, JNTUH, UoH, KU, TU, SU, PU, IIIT-H), 1,043 students (Telugu names + roll numbers), 133 professors, 36 admins, 9,228 marks, 24,608 attendance records, invoices/payments/payslips/hall-tickets/expenses.

## Implemented (June 2026)
- **Super Admin dashboard** (`/super`): platform KPIs; list all universities with student/professor counts; create university; toggle AI; suspend/activate. Role: `super_admin`.
- **Tenant Admin dashboard** (`/tenant`): per-university KPIs (students, professors, departments, courses, fees collected/pending, expenses, payroll) + 6 tabs (Students, Professors, Payments, Payroll, Hall Tickets, Expenses), all tenant-scoped. Role: `admin`.
- **Auth:** login, /me, ProtectedRoute, role-based redirects, logout. Tested: 23/23 backend, 100% frontend flows, role isolation (403/401) verified.

## Backlog / Next Action Items
- **P0:** Student dashboard + Professor dashboard (the other two roles).
- **P1:** Student AI assistant (LLM + RAG over professor notes) — needs notes ingestion + vector store + LLM integration.
- **P1:** SSO (SAML/OIDC) alongside JWT; password reset.
- **P2:** Charts/analytics on dashboards (deferred per user — "no charts for now"); CSV export; pagination on large tables.
- **P2:** Migrate sandbox DB to managed PostgreSQL for production; Alembic migrations; RLS policies.
- **P2:** Per-tenant branding, payment gateway integration (Stripe/Razorpay), notifications.

## Credentials
See `/app/memory/test_credentials.md`.
