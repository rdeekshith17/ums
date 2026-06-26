# UniAI — Multi-Tenant University AI Dashboard
## System Architecture Document

**Version:** 1.0
**Date:** June 2026
**Prepared for:** Project Lead / Manager
**Document type:** Architecture blueprint (no implementation code)

---

## 1. Executive Summary

UniAI is a **multi-tenant SaaS platform** that gives universities an AI-powered
dashboard serving three distinct user roles — **Students**, **Professors**, and
**Administration**. Each tenant (university) is logically isolated. The platform
combines a **RAG (Retrieval-Augmented Generation) AI assistant** grounded on
professor-uploaded notes for students, an **academic analytics engine** for
professors, and an **operations/finance console** for administration.

**Key architectural decisions (from requirements):**

| Decision Area | Choice |
|---|---|
| Tenancy model | Multi-university, multi-tenant SaaS |
| LLM strategy | Hybrid — self-hosted open-source (default) + OpenAI (premium/fallback) |
| Authentication | Dual: University SSO (SAML/OIDC) + Custom Email-Password (JWT) |
| Payments/Payroll | Abstracted behind a provider interface — gateway integration deferred |
| RBAC | 3 primary roles + tenant scoping + fine-grained permissions |

---

## 2. Goals, Non-Goals & Constraints

### 2.1 Goals
- One platform, three role-specific experiences, isolated per university.
- Student AI assistant that answers **only** from authorized course material (RAG).
- Professor analytics on attendance, marks, performance trends, and weak-area detection.
- Admin console for payments, payroll, hall tickets, and expense tracking.
- Horizontally scalable to support many universities concurrently.

### 2.2 Non-Goals (v1)
- Full LMS replacement (assignment grading workflows, video conferencing).
- Mobile native apps (responsive web first; mobile in later phase).
- Real payment gateway go-live (interface ready, provider chosen later).

### 2.3 Constraints
- Data isolation and privacy (FERPA/GDPR-style) are mandatory across tenants.
- AI answers must be **grounded and auditable** (no hallucinated grades/policy).
- Cost control: route most LLM traffic to self-hosted models, OpenAI on demand.

---

## 3. Stakeholders & User Personas

| Persona | Role | Primary Needs |
|---|---|---|
| **Student** | End user | Ask questions on course notes, view own attendance/marks, study help |
| **Professor** | Educator | Upload notes, track class attendance & marks, identify lagging students |
| **Admin/Registrar** | Operations | Fees/payments, payroll, hall tickets, expense ledger, reports |
| **University Super-Admin** | Tenant owner | Manage users, roles, departments, integrations, branding |
| **Platform Operator** | UniAI (you) | Provision tenants, monitor, bill universities, platform health |

---

## 4. High-Level System Architecture

```
                        ┌──────────────────────────────────────────────┐
                        │                  CLIENTS                       │
                        │   Student Web │ Professor Web │ Admin Web      │
                        │     (React SPA, role-aware, responsive)        │
                        └───────────────────────┬────────────────────────┘
                                                │ HTTPS
                                                ▼
                        ┌──────────────────────────────────────────────┐
                        │            API GATEWAY / EDGE                  │
                        │  TLS · Rate limit · WAF · Tenant resolver      │
                        │  (subdomain/header → tenant_id) · Routing      │
                        └───────────────────────┬────────────────────────┘
                                                │
              ┌──────────────────┬─────────────┼──────────────┬───────────────────┐
              ▼                  ▼             ▼              ▼                   ▼
       ┌────────────┐    ┌──────────────┐ ┌──────────┐ ┌─────────────┐   ┌──────────────┐
       │   AUTH &   │    │  ACADEMIC    │ │   AI /   │ │   FINANCE/   │   │   TENANT &   │
       │   RBAC     │    │  SERVICE     │ │   RAG    │ │   ADMIN OPS  │   │   ADMIN MGMT │
       │  SVC       │    │ (attendance, │ │ SERVICE  │ │ (payments,   │   │ (provision,  │
       │ SSO+JWT    │    │  marks,      │ │          │ │  payroll,    │   │  users,      │
       │            │    │  analytics)  │ │          │ │  halltickets,│   │  branding)   │
       └─────┬──────┘    └──────┬───────┘ └────┬─────┘ │  expenses)   │   └──────┬───────┘
             │                  │              │       └──────┬───────┘          │
             │                  │              │              │                  │
             └──────────────────┴──────┬───────┴──────────────┴──────────────────┘
                                        │
        ┌───────────────────────────────┼───────────────────────────────────────────┐
        ▼                ▼               ▼                 ▼               ▼           ▼
 ┌────────────┐  ┌──────────────┐ ┌───────────┐  ┌──────────────┐ ┌──────────┐ ┌──────────┐
 │  Primary   │  │   Vector     │ │  Object   │  │   Cache /    │ │  Message │ │  Audit/  │
 │  DB        │  │   DB         │ │  Storage  │  │   Queue      │ │  Broker  │ │  Log DB  │
 │ (Postgres/ │  │ (pgvector/   │ │ (S3-like, │  │ (Redis)      │ │ (Kafka/  │ │          │
 │  Mongo)    │  │  Qdrant)     │ │  notes)   │  │              │ │  RabbitMQ│ │          │
 └────────────┘  └──────────────┘ └───────────┘  └──────────────┘ └──────────┘ └──────────┘

                         ┌─────────────────────────────────────────┐
                         │        AI INFERENCE LAYER                 │
                         │  Self-hosted LLM (vLLM/Ollama, Llama-3)   │
                         │  + Embedding model (bge/e5)               │
                         │  + OpenAI API (premium / fallback)        │
                         │  Router decides per-tenant / per-query    │
                         └─────────────────────────────────────────┘
```

---

## 5. Multi-Tenancy Architecture

**Model chosen: Shared application + tenant-scoped data (hybrid isolation).**

| Layer | Isolation Strategy |
|---|---|
| Application/compute | Shared stateless services; `tenant_id` injected in every request context |
| Relational data | Shared DB with mandatory `tenant_id` on every row + Row-Level Security (RLS); **schema-per-tenant or DB-per-tenant** option for enterprise/premium universities |
| Vector data | Per-tenant collections/namespaces in the vector DB (hard partition) |
| Object storage | Per-tenant bucket prefix `/{tenant_id}/...` with scoped access policies |
| Tenant resolution | Subdomain (`mit.uniai.app`) or custom domain → `tenant_id` at the gateway |

**Why hybrid:** shared infrastructure keeps cost low for the long tail of
universities, while DB-per-tenant can be offered to large institutions needing
strict physical isolation or data residency — without changing app code.

**Tenant lifecycle:** Provision → Configure (branding, SSO, departments) →
Seed admin users → Active → Suspend/Archive. Each step is an idempotent
operation in the Tenant Management service.

---

## 6. Service / Component Breakdown

### 6.1 Auth & RBAC Service
- Dual auth: **SSO** (SAML 2.0 / OIDC for Google Workspace, Microsoft Entra) and
  **email-password** with JWT access + refresh tokens.
- Issues short-lived JWTs carrying `{ user_id, tenant_id, role, permissions[] }`.
- Central **policy engine** (RBAC + attribute checks). Roles: `student`,
  `professor`, `admin`, `super_admin`, `platform_operator`.
- Handles MFA, password reset, session revocation, SSO ↔ local account linking.

### 6.2 Academic Service (Professor & Student data)
- Domain: courses, sections, enrollments, attendance, assessments, marks.
- **Analytics sub-engine**: computes per-student performance trends, class
  averages, percentile ranking, and **weak-area / lagging detection** (subject
  or topic where a student trends below threshold or below class mean).
- Exposes read APIs for professor dashboards and student self-view.

### 6.3 AI / RAG Service
- **Ingestion pipeline**: professor uploads notes → parse (PDF/DOCX/PPT/text) →
  chunk → embed → store vectors with metadata (`tenant_id, course_id, prof_id,
  visibility`).
- **Query pipeline**: student question → embed → vector search (tenant + course
  scoped) → re-rank → assemble grounded prompt → LLM → answer **with citations**
  back to source notes.
- **Guardrails**: refuse out-of-scope questions, no answers without retrieved
  context, content moderation, no leaking of other tenants'/courses' material.
- **Model router**: default self-hosted model; escalate to OpenAI for complex
  queries, long context, or as fallback on capacity limits.

### 6.4 Finance / Admin Ops Service
- Modules: **Payments** (student fees), **Payroll** (professor salaries),
  **Hall Tickets** (exam admit-card generation/eligibility), **Expenses**
  (university expense ledger & budgets).
- **Payment provider abstraction**: a `PaymentProvider` interface (charge,
  refund, payout, webhook) with a no-op/manual ledger implementation now;
  Stripe/Razorpay/PayPal pluggable later without touching business logic.
- Generates invoices, receipts, payslips, hall-ticket PDFs, and finance reports.

### 6.5 Tenant & Admin Management Service
- Tenant provisioning, branding/theming, SSO config, department & program setup,
  bulk user import (CSV/SIS sync), feature flags, per-tenant LLM preferences.

### 6.6 Notification Service (cross-cutting)
- Email/SMS/in-app for fee dues, payslip ready, attendance alerts, AI digest.
- Pluggable providers (SendGrid/Resend/Twilio) behind an interface.

### 6.7 Reporting & Audit Service
- Immutable audit log of sensitive actions (mark edits, payments, role changes).
- Scheduled reports and exports; powers compliance reviews.

---

## 7. Data Model (Core Entities)

> All entities carry `tenant_id`, `created_at`, `updated_at`. IDs are UUIDs.

```
Tenant(id, name, domain, sso_config, branding, plan, status)
User(id, tenant_id, name, email, auth_type[sso|local], status)
Role(id, tenant_id, name)  ── UserRole(user_id, role_id)
Permission(id, key)        ── RolePermission(role_id, permission_id)

Department(id, tenant_id, name)
Program(id, tenant_id, department_id, name)
Course(id, tenant_id, program_id, code, title, professor_id)
Section(id, course_id, term, schedule)
Enrollment(id, section_id, student_id, status)

AttendanceRecord(id, section_id, student_id, date, status[present|absent|late])
Assessment(id, section_id, type, max_marks, weight, date)
Mark(id, assessment_id, student_id, score, graded_by)
PerformanceSnapshot(id, student_id, course_id, period, metrics_json, weak_areas[])

Note(id, tenant_id, course_id, professor_id, title, file_ref, visibility, status)
DocumentChunk(id, note_id, chunk_index, text, token_count)   # source of truth
VectorEntry(chunk_id, embedding, metadata)                   # in vector DB
ChatSession(id, student_id, course_id) ── ChatMessage(id, session_id, role, content, citations[])

Invoice(id, tenant_id, student_id, items[], amount, status, due_date)
Payment(id, invoice_id, amount, method, provider_ref, status)
PayrollRun(id, tenant_id, period, status)
Payslip(id, payroll_run_id, professor_id, gross, deductions, net)
HallTicket(id, tenant_id, student_id, exam_id, eligibility, file_ref)
Expense(id, tenant_id, category, amount, vendor, date, approved_by)

AuditLog(id, tenant_id, actor_id, action, target, before, after, ts)
```

**Storage placement:**
- Relational (Postgres recommended): users, academics, finance, audit — needs ACID + RLS.
- Vector DB (pgvector / Qdrant / Milvus): embeddings, per-tenant namespaces.
- Object storage (S3-compatible): raw note files, generated PDFs, payslips.
- Redis: sessions, rate limits, hot analytics cache.

---

## 8. API Surface (Representative, REST/JSON, all `/api` prefixed)

**Auth**
```
POST /api/auth/login            POST /api/auth/refresh
POST /api/auth/sso/callback     POST /api/auth/logout
```
**Student**
```
GET  /api/me/attendance         GET  /api/me/marks         GET /api/me/performance
POST /api/ai/chat               GET  /api/ai/sessions/:id  GET /api/courses/:id/notes
```
**Professor**
```
POST /api/notes                 (upload)        DELETE /api/notes/:id
GET  /api/sections/:id/attendance               POST   /api/attendance
GET  /api/sections/:id/marks                    POST   /api/marks
GET  /api/sections/:id/analytics                GET    /api/students/:id/weak-areas
```
**Admin**
```
GET/POST /api/invoices          POST /api/payments        GET /api/finance/reports
GET/POST /api/payroll/runs      GET  /api/payslips/:id
POST     /api/halltickets/generate              GET /api/halltickets/:id
GET/POST /api/expenses
```
**Tenant/Super-Admin**
```
POST /api/tenant/provision      PUT /api/tenant/branding   PUT /api/tenant/sso
POST /api/users/import          POST /api/users  PUT /api/users/:id/roles
```

Every request validated against `tenant_id` + role + permission before reaching domain logic.

---

## 9. Key Data Flows

### 9.1 Student RAG Query
```
Student asks question
  → Gateway resolves tenant, validates JWT (role=student)
  → AI Service embeds query
  → Vector search scoped to {tenant_id, enrolled course_ids, visibility=allowed}
  → Re-rank top-K chunks → build grounded prompt
  → Model Router: self-hosted LLM (default) or OpenAI (escalation/fallback)
  → Answer + citations to source notes → stored in ChatMessage → returned
  → Audit log entry
```

### 9.2 Professor Notes Ingestion
```
Professor uploads file
  → Stored in object storage /{tenant_id}/courses/{course_id}/
  → Async job (queue): parse → chunk → embed → upsert into tenant's vector namespace
  → Note.status = ready  → now retrievable by enrolled students only
```

### 9.3 Performance / Weak-Area Detection
```
Attendance + Marks updated
  → Analytics job recomputes PerformanceSnapshot per student/course
  → Flags weak areas (score < threshold OR < class_mean - σ, attendance < policy)
  → Surfaced on professor dashboard + student self-view
```

### 9.4 Admin Payment (provider-abstracted)
```
Admin issues invoice → student pays
  → PaymentProvider.charge() [manual/ledger now; gateway later]
  → Webhook/confirmation → Payment.status=paid → receipt PDF → notification
  → Audit log
```

---

## 10. Recommended Technology Stack

| Layer | Recommendation | Rationale |
|---|---|---|
| Frontend | React (SPA), role-based routing, responsive | Single codebase, role-aware UI |
| API services | Python (FastAPI) microservices or modular monolith | Async, great AI/ML ecosystem |
| Primary DB | PostgreSQL + Row-Level Security | ACID, native multi-tenant RLS, pgvector option |
| Vector DB | pgvector (start) → Qdrant/Milvus (scale) | Per-tenant namespaces, hybrid search |
| Object storage | S3-compatible (MinIO/S3) | Notes, PDFs, payslips |
| Cache/sessions | Redis | Low-latency, rate limiting |
| Async/queue | RabbitMQ or Kafka | Ingestion, analytics, payroll jobs |
| LLM serving | vLLM / Ollama hosting Llama-3 (or similar) + embeddings (bge/e5) | Cost-efficient default |
| External LLM | OpenAI API | Premium quality / fallback |
| Auth | OIDC/SAML libs + JWT | Dual auth requirement |
| Gateway | API gateway (Kong/Nginx/Traefik) + WAF | TLS, routing, tenant resolution |
| Deployment | Docker + Kubernetes | Horizontal scaling, isolation |
| Observability | Prometheus + Grafana + centralized logs + tracing | Health & cost monitoring |

> Note: a **modular monolith** is recommended for v1 (faster to build, easier to
> operate), with clean service boundaries so it can be split into microservices
> as load grows. The diagram above shows the target logical decomposition.

---

## 11. Security, Privacy & Compliance

- **Tenant isolation:** RLS on every table; tenant-scoped vector namespaces and
  storage prefixes; deny-by-default authorization.
- **AuthN/Z:** short-lived JWTs, refresh rotation, MFA, SSO; least-privilege RBAC.
- **Data protection:** TLS in transit, encryption at rest, PII field-level
  encryption for sensitive finance/identity data.
- **AI safety:** strict RAG grounding, citations, refusal on no-context,
  cross-tenant leakage tests, prompt-injection defenses, moderation.
- **Auditability:** immutable audit log for marks, payments, role/permission changes.
- **Compliance posture:** FERPA/GDPR-aligned — data residency option via
  DB-per-tenant, right-to-erasure workflows, retention policies, consent records.
- **Secrets:** managed via vault/secret store; no secrets in code or client.

---

## 12. Scalability & Reliability

- **Stateless services** behind a load balancer → horizontal autoscaling.
- **Async workers** for heavy jobs (embedding, analytics, payroll) decouple from request path.
- **Read scaling:** DB read replicas + Redis caching for dashboards/analytics.
- **AI scaling:** GPU node pool for self-hosted inference with autoscaling;
  OpenAI absorbs burst/overflow; per-tenant rate limits & quotas.
- **Vector scaling:** start pgvector, migrate to dedicated Qdrant/Milvus cluster
  as embedding volume grows; sharding by tenant.
- **Resilience:** circuit breakers around LLM/payment providers, retries with
  backoff, dead-letter queues, graceful degradation (cached answers, queued jobs).
- **DR/Backups:** automated DB + object storage backups, point-in-time recovery,
  multi-AZ deployment.

---

## 13. Environments & DevOps

- Environments: `dev` → `staging` → `production`, each tenant-aware.
- CI/CD: automated tests (incl. cross-tenant isolation tests), containerized builds, blue-green/canary deploys.
- IaC: declarative infra (Terraform/Helm) for reproducible tenant + cluster setup.
- Cost controls: dashboards for LLM token spend per tenant; budget alerts; route policy self-hosted-first.

---

## 14. Phased Delivery Roadmap

| Phase | Theme | Scope | Outcome |
|---|---|---|---|
| **0 — Foundations** | Platform skeleton | Multi-tenant core, dual auth (JWT+SSO), RBAC, tenant provisioning, base UI shells for 3 roles | Tenants can be created; users log in with correct role views |
| **1 — Academic core** | Professor & student data | Courses/sections/enrollment, attendance, marks entry, student self-view dashboards | Professors record data; students see their own records |
| **2 — Student AI (RAG)** | Notes + AI assistant | Note ingestion pipeline, vector store, RAG query with citations, self-hosted LLM + OpenAI router, guardrails | Students get grounded AI help on course notes |
| **3 — Analytics** | Performance intelligence | Performance snapshots, class analytics, weak-area/lagging detection, professor insights dashboard | Professors identify where students lag |
| **4 — Admin Ops** | Finance & operations | Invoices, expenses ledger, payroll runs/payslips, hall-ticket generation; payment **interface** (manual/ledger) | Admin runs operations end-to-end without a live gateway |
| **5 — Payments go-live** | Gateway integration | Plug chosen provider (Stripe/Razorpay/PayPal) into the payment interface, webhooks, reconciliation | Real fee collection & payouts |
| **6 — Hardening & scale** | Production readiness | Observability, autoscaling, DR, compliance workflows, mobile-responsive polish | Enterprise-ready, multi-university scale |

**Critical path dependency:** Phase 0 → 1 → (2 and 3 in parallel) → 4 → 5 → 6.

---

## 15. Key Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Cross-tenant data leak | Severe (trust/compliance) | RLS, scoped namespaces, automated isolation tests in CI |
| AI hallucination on grades/policy | High | Strict RAG grounding + citations + refusal on no-context |
| LLM cost overrun | Medium | Self-hosted-first routing, quotas, per-tenant token budgets |
| SSO heterogeneity across universities | Medium | Standardize on OIDC/SAML; per-tenant SSO config |
| Payment provider lock-in | Medium | Provider abstraction interface; defer & keep pluggable |
| Scaling vector search | Medium | Start pgvector, clear migration path to Qdrant/Milvus |

---

## 16. Open Decisions (to confirm later)

1. Payment provider(s) and regions (Stripe vs Razorpay vs PayPal) — Phase 5.
2. Self-hosted model choice & GPU budget (Llama-3 variant, context length).
3. Microservices vs modular monolith for v1 (recommendation: modular monolith).
4. Data residency requirements per university (drives shared-DB vs DB-per-tenant).
5. SIS/ERP integrations needed (student information system sync).

---

*End of architecture document. No application code included — this is a design
blueprint intended to guide build planning and team alignment.*
