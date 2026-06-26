from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# Base styles
styles = doc.styles
normal = styles['Normal']
normal.font.name = 'Calibri'
normal.font.size = Pt(11)

def add_heading(text, level=1):
    h = doc.add_heading(text, level=level)
    return h

def add_para(text, bold=False, italic=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    return p

def add_bullet(text):
    doc.add_paragraph(text, style='List Bullet')

def add_code_block(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.name = 'Consolas'
    r.font.size = Pt(8.5)
    return p

def add_table(headers, rows):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = 'Light Grid Accent 1'
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        for par in hdr[i].paragraphs:
            for run in par.runs:
                run.bold = True
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = val
    return t

# ===== Title =====
title = doc.add_heading('Project Skeleton — Ownership Map (Corrected)', level=0)
add_para('Who builds what, how the team rotates for whole-project experience, and the phase-wise plan', italic=True)

add_para('Stack: FastAPI + SQLAlchemy (ORM) + Alembic (migrations) + Jinja2 templates + Bootstrap (Admin UI) + Docker/Docker-Compose.')
add_para('Scope of this skeleton: Tenant Management, AI Launch & Session, Admin UI, and Infra/QA foundations.')
add_para('Ownership philosophy (updated): Collective ownership with rotation. No file is permanently locked to one squad. Each module has a rotating Primary (builds) and Reviewer (reviews + learns), and developers rotate across modules each phase so every team member gets hands-on experience across the whole project.', italic=True)

# ===== Section 1: Tree =====
add_heading('1. Annotated Project Tree (corrected nesting)', 1)
tree = """project-root/
├── app/
│   ├── main.py                     # Bootstrap FastAPI app + register all routers
│   ├── config.py                   # Centralized settings (.env: DB URL, JWT secret, env)
│   ├── database.py                 # SQLAlchemy engine + session maker (shared by models)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── tenant.py               # Tenant ORM model
│   │   ├── session.py              # Session ORM model
│   │   └── audit_log.py            # AuditLog ORM model (all modules emit events)
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── tenant.py               # Pydantic schemas for /tenants + enable/disable-ai
│   │   ├── launch.py               # Schema for POST /api/v1/ai/launch
│   │   └── session.py              # Schema for session create/response
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── tenants.py              # Tenant CRUD + PATCH enable-ai / disable-ai
│   │   ├── launch.py               # POST /api/v1/ai/launch
│   │   ├── admin.py                # Jinja page routes (dashboard, list, add, edit)
│   │   └── health.py               # Readiness / liveness checks
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── tenant_service.py       # Tenant CRUD + AI enable/disable business logic
│   │   ├── launch_service.py       # Orchestrates validate -> session -> token -> chat URL
│   │   └── token_service.py        # JWT signing, claims, expiry
│   │
│   ├── templates/
│   │   ├── layout.html             # Base layout + nav
│   │   ├── tenants.html            # Tenant list + dashboard stats
│   │   ├── add_tenant.html         # Create tenant form
│   │   └── edit_tenant.html        # Edit tenant + Enable/Disable AI buttons
│   │
│   └── static/
│       ├── css/
│       │   └── style.css           # Bootstrap-based styling
│       └── js/
│           └── app.js              # Client-side interactivity (buttons/forms)
│
├── migrations/                     # Alembic migration scripts (tenants, sessions, audit_logs)
├── tests/
│   ├── test_tenants.py             # Tenant CRUD + enable/disable tests
│   └── test_launch.py              # Launch + full create->enable->launch->token flow
├── Dockerfile                      # Container image for the app
├── docker-compose.yml              # App + database wired for local/staging
├── requirements.txt                # Python deps (every dev adds what their part needs)
├── .env.example                    # Sample environment variables
└── README.md                       # Setup, architecture overview, endpoint list"""
add_code_block(tree)

# ===== Section 2: Data Model =====
add_heading('2. Data Model Snapshot (for reference)', 1)
add_table(
    ['Table', 'Key Columns'],
    [
        ['tenants', 'id, tenant_id, tenant_name, portal_url, status, ai_enabled, created_at'],
        ['sessions', 'id, session_id, tenant_id, user_id, role, expires_at, created_at'],
        ['audit_logs', 'id, tenant_id, event_type, details, created_at'],
    ]
)

# ===== Section 3: Build Plan =====
add_heading('3. File-by-File Build Plan (one-week sprint, Day 1-5)', 1)
add_table(
    ['File / Folder', 'Phase', 'What to Build', 'Sprint Day'],
    [
        ['app/main.py', 'Foundation', "Bootstrap FastAPI app; register each router as it lands (tenants, launch, admin, health)", 'Day 1-5'],
        ['app/config.py', 'Foundation', 'Centralized settings - DB URL, JWT secret, env vars from .env', 'Day 1'],
        ['app/database.py', 'Foundation', 'SQLAlchemy engine + session maker used by all models', 'Day 1'],
        ['app/models/tenant.py', 'Core', 'Tenant ORM model', 'Day 1-2'],
        ['app/models/session.py', 'Core', 'Session ORM model', 'Day 2'],
        ['app/models/audit_log.py', 'Foundation', 'AuditLog ORM model; tenant & launch flows write events here', 'Day 1 (used 3-5)'],
        ['app/schemas/tenant.py', 'Core', 'Pydantic schemas for POST/GET/PUT/DELETE /tenants + enable/disable-ai', 'Day 2'],
        ['app/schemas/launch.py', 'Core', 'Schema for POST /api/v1/ai/launch (tenant_id in -> chat URL + token out)', 'Day 2'],
        ['app/schemas/session.py', 'Core', 'Session create/response schema (session_id, expires_at, role)', 'Day 2-3'],
        ['app/routes/tenants.py', 'Core', 'Tenant CRUD + PATCH enable-ai/disable-ai -> calls tenant_service.py', 'Day 2-3'],
        ['app/routes/launch.py', 'Core', 'POST /api/v1/ai/launch -> validate tenant, call launch + token services', 'Day 2-4'],
        ['app/routes/admin.py', 'Core', 'Jinja page routes (dashboard, list, add, edit) -> calls Tenant API', 'Day 2-4'],
        ['app/routes/health.py', 'Hardening', 'Readiness/liveness endpoints', 'Day 5'],
        ['app/services/tenant_service.py', 'Core', 'Tenant CRUD + AI toggle logic: validation, DB writes, audit calls', 'Day 2-3'],
        ['app/services/launch_service.py', 'Core', 'Validate tenant + ai_enabled, create session, call token service, return chat URL', 'Day 3-4'],
        ['app/services/token_service.py', 'Core', 'JWT generation - signing, claims (tenant_id, session_id, role), expiry', 'Day 3-4'],
        ['app/templates/*.html', 'Core', 'layout.html, tenants.html, add_tenant.html, edit_tenant.html', 'Day 2-3'],
        ['app/static/css, js', 'Core', 'Bootstrap styling + client-side interactivity', 'Day 2-5'],
        ['migrations/', 'Foundation', 'Alembic scripts for 3 tables; rerun on any model change', 'Day 1, 3'],
        ['tests/test_tenants.py', 'Integration', 'Automated tests for all Tenant CRUD + enable/disable', 'Day 3-4'],
        ['tests/test_launch.py', 'Integration', 'Tests for launch + full create->enable->launch->token flow', 'Day 3-4'],
        ['Dockerfile / docker-compose.yml', 'Foundation', 'Containerize app; Compose wires app + DB', 'Day 1-2, 5'],
        ['requirements.txt / .env.example', 'Ongoing', 'Maintained centrally; every dev adds packages/env vars their part needs', 'Ongoing'],
        ['README.md', 'Foundation/Hardening', 'Setup, architecture, endpoint list - updated as pieces land', 'Day 1, 5'],
    ]
)

# ===== Section 4: Ownership Model =====
add_heading('4. Cross-Functional Ownership Model (everyone learns the whole project)', 1)
add_para('Principle: We replace fixed silos with collective ownership + rotation. Every developer rotates through all four areas over the project so that, by the end, each team member has built, reviewed, and tested every layer (models -> schemas -> routes -> services -> templates -> infra/tests).')

add_heading('4.1 Roles per module (rotating)', 2)
add_bullet('Primary (P): builds the module this phase.')
add_bullet('Reviewer (R): reviews PRs, pairs, and learns the module - becomes next phase Primary.')
add_bullet('Lead: owns main.py scaffold + architecture, unblocks, enforces standards.')

add_heading('4.2 Rotation matrix (Primary focus per phase)', 2)
add_para('Devs are grouped into 4 pods (2-3 devs each). Pods shift one module to the right every phase, so each pod touches every area.')
add_table(
    ['Phase', 'Pod 1', 'Pod 2', 'Pod 3', 'Pod 4'],
    [
        ['Phase 1 - Foundation', 'Tenant models/schemas', 'Session + token services', 'Admin UI scaffolding', 'Infra: config, DB, Docker, migrations'],
        ['Phase 2 - Core build', 'Tenant routes + service', 'Launch route + service', 'Admin templates + static', 'Audit log + health + tests setup'],
        ['Phase 3 - Integration', 'Launch route + service', 'Admin templates + static', 'Infra/tests', 'Tenant routes + service'],
        ['Phase 4 - Hardening', 'Infra/tests + health', 'Tenant routes + service', 'Launch route + service', 'Admin UI polish + docs'],
    ]
)
add_para('After 4 phases, every pod has worked on Tenant, Launch/Session, Admin UI, and Infra/QA. Pair-programming across pods is encouraged on integration days.', italic=True)

add_heading('4.3 Guardrails so rotation does not cause chaos', 2)
add_bullet('One coding standard (linter/formatter + naming conventions) enforced in CI.')
add_bullet('Mandatory PR review by the incoming Primary - that is how knowledge transfers.')
add_bullet('Module README/doc-string kept up to date by whoever is Primary that phase.')
add_bullet('main.py and requirements.txt changes always reviewed by the Lead to avoid merge conflicts.')
add_bullet('Daily 15-min sync where each pod demos what they shipped, so the whole team stays current on all modules.')

# ===== Section 5: Phases =====
add_heading('5. Phase-Wise Work Breakdown', 1)

add_heading('Phase 1 - Foundation (Day 1)', 2)
add_para('Goal: Skeleton runs end-to-end empty.', bold=True)
for b in ['config.py, database.py (engine + session).',
          'All three ORM models defined (tenant, session, audit_log).',
          'First Alembic migration creates the 3 tables.',
          'Dockerfile + docker-compose.yml boot app + DB locally.',
          'main.py boots an empty FastAPI app.']:
    add_bullet(b)
add_para('Exit criteria: docker-compose up starts the app; DB tables exist; health stub responds.', italic=True)

add_heading('Phase 2 - Core Modules (Day 2-3)', 2)
add_para('Goal: Each functional area works in isolation.', bold=True)
for b in ['Tenant: schemas -> service -> routes (CRUD + enable/disable-ai), writing audit events.',
          'Launch/Session: schemas -> token_service (JWT) -> launch_service -> /api/v1/ai/launch.',
          'Admin UI: Jinja templates + Bootstrap + app.js; pages call the Tenant API.']:
    add_bullet(b)
add_para('Exit criteria: Tenant CRUD works via API; admin pages render; launch returns a token.', italic=True)

add_heading('Phase 3 - Integration (Day 3-4)', 2)
add_para('Goal: Modules talk to each other; full flow proven.', bold=True)
for b in ['Wire all routers into main.py.',
          'End-to-end flow: create tenant -> enable AI -> launch -> receive chat URL + token.',
          'Admin UI buttons trigger enable/disable and reflect status.',
          'tests/test_tenants.py + tests/test_launch.py cover CRUD and the full flow.']:
    add_bullet(b)
add_para('Exit criteria: Full create->enable->launch->token flow passes automated tests.', italic=True)

add_heading('Phase 4 - Hardening & Handover (Day 5)', 2)
add_para('Goal: Production-ready skeleton.', bold=True)
for b in ['health.py readiness/liveness endpoints.',
          'Error handling, input validation, and audit-log coverage reviewed.',
          'docker-compose.yml finalized for staging; .env.example complete.',
          'README.md finalized (setup, architecture, endpoint list).',
          'Knowledge-share session: each pod walks the others through its module.']:
    add_bullet(b)
add_para('Exit criteria: All tests green; docs complete; every team member can explain every module.', italic=True)

# ===== Section 6: Quick reference =====
add_heading('6. Quick Reference - Module Areas (no permanent owners)', 1)
add_table(
    ['Area', 'Files', 'Notes'],
    [
        ['Tenant Management', 'models/tenant.py, schemas/tenant.py, routes/tenants.py, services/tenant_service.py', 'Rotates each phase'],
        ['Launch & Session', 'models/session.py, schemas/launch.py, schemas/session.py, routes/launch.py, services/launch_service.py, services/token_service.py', 'Rotates each phase'],
        ['Admin UI', 'routes/admin.py, templates/*, static/*', 'Rotates each phase'],
        ['Infrastructure & QA', 'config.py, database.py, models/audit_log.py, routes/health.py, migrations/, tests/, Dockerfile, docker-compose.yml, requirements.txt, .env.example', 'Rotates each phase'],
        ['Architecture (Lead)', 'main.py, README.md', 'Stable lead role; standards & integration'],
    ]
)

add_para('Corrected version: fixed tree nesting/connectors, added missing __init__.py and proper static/ subfolders, resolved path inconsistencies between sections, normalized sprint days, replaced hard silos with a rotation model giving every team member whole-project experience, and added a phase-wise work breakdown.', italic=True)

out = '/app/scripts/Project_Skeleton_Ownership_Map_CORRECTED.docx'
doc.save(out)
print('Saved:', out)
