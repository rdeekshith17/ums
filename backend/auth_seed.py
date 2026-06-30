"""Create login accounts for the dashboards and write test credentials.

- 1 super_admin (platform operator).
- Sets a known password on every existing tenant admin (role='admin').

Run:  cd /app/backend && python auth_seed.py
"""

from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from sqlalchemy import inspect, text  # noqa: E402

import app.models as m  # noqa: E402
from app.auth import hash_password  # noqa: E402
from app.database import SessionLocal, engine  # noqa: E402

SUPER_EMAIL = "superadmin@uniai.app"
SUPER_PW = "SuperAdmin@123"
TENANT_PW = "Admin@123"


def run():
    # Ensure auth columns exist (works on SQLite and Postgres).
    cols = {c["name"] for c in inspect(engine).get_columns("users")}
    with engine.begin() as conn:
        if "password_hash" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR"))
        if "last_login" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN last_login TIMESTAMP"))

    db = SessionLocal()

    su = db.query(m.User).filter(m.User.email == SUPER_EMAIL).first()
    if su:
        su.password_hash = hash_password(SUPER_PW)
        su.role = "super_admin"
    else:
        db.add(m.User(
            tenant_id="PLATFORM", full_name="Platform Super Admin",
            email=SUPER_EMAIL, role="super_admin", auth_type="local",
            password_hash=hash_password(SUPER_PW),
        ))

    admins = db.query(m.User).filter(m.User.role == "admin").all()
    pw = hash_password(TENANT_PW)
    for a in admins:
        a.password_hash = pw
    db.commit()

    demo = (db.query(m.User, m.University)
            .join(m.University, m.University.tenant_id == m.User.tenant_id)
            .filter(m.User.role == "admin")
            .order_by(m.User.email).first())
    demo_email = demo[0].email if demo else "(none)"
    demo_uni = demo[1].name if demo else ""

    write_credentials(demo_email, demo_uni, len(admins))
    print(f"super_admin: {SUPER_EMAIL} / {SUPER_PW}")
    print(f"tenant admins updated: {len(admins)} (password '{TENANT_PW}')")
    print(f"demo tenant admin: {demo_email}  [{demo_uni}]")
    db.close()


def write_credentials(demo_email, demo_uni, count):
    content = f"""# Test Credentials — UniAI Dashboards

## Super Admin (platform operator — manages all universities)
- Email: {SUPER_EMAIL}
- Password: {SUPER_PW}
- Role: super_admin

## Tenant Admin (university admin — manages one university)
All {count} seeded university admins share this password: **{TENANT_PW}**

Demo tenant admin account:
- Email: {demo_email}
- Password: {TENANT_PW}
- University: {demo_uni}

(Any admin email from admins.csv works with the password {TENANT_PW}.)

## Auth endpoints
- POST /api/auth/login   body: {{"email","password"}}  -> {{access_token, user}}
- GET  /api/auth/me      header: Authorization: Bearer <token>
"""
    path = Path("/app/memory/test_credentials.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


if __name__ == "__main__":
    run()
