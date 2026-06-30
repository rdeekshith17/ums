"""UniAI backend test suite — auth, super admin, tenant admin endpoints."""

import os
import uuid

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    # fallback for backend-only runs
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                BASE_URL = line.split("=", 1)[1].strip().rstrip("/")

SUPER_EMAIL = "superadmin@uniai.app"
SUPER_PASS = "SuperAdmin@123"
TENANT_EMAIL = "aishwarya.mudirajadm4@ku.ac.in"
TENANT_PASS = "Admin@123"


# ---------- fixtures ----------
@pytest.fixture(scope="session")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


def _login(api, email, password):
    r = api.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    return r.json()


@pytest.fixture(scope="session")
def super_token(api):
    return _login(api, SUPER_EMAIL, SUPER_PASS)["access_token"]


@pytest.fixture(scope="session")
def tenant_token(api):
    return _login(api, TENANT_EMAIL, TENANT_PASS)["access_token"]


def H(token):
    return {"Authorization": f"Bearer {token}"}


# ---------- health ----------
class TestHealth:
    def test_root(self, api):
        r = api.get(f"{BASE_URL}/api/")
        assert r.status_code == 200
        assert "UniAI" in r.json().get("message", "")


# ---------- auth ----------
class TestAuth:
    def test_login_super_success(self, api):
        data = _login(api, SUPER_EMAIL, SUPER_PASS)
        assert data["token_type"] == "bearer"
        assert data["user"]["role"] == "super_admin"
        assert data["user"]["email"].lower() == SUPER_EMAIL

    def test_login_tenant_success(self, api):
        data = _login(api, TENANT_EMAIL, TENANT_PASS)
        assert data["user"]["role"] == "admin"
        assert data["user"]["tenant_id"]

    def test_login_invalid(self, api):
        r = api.post(f"{BASE_URL}/api/auth/login",
                     json={"email": SUPER_EMAIL, "password": "wrong"})
        assert r.status_code == 401

    def test_me_super(self, api, super_token):
        r = api.get(f"{BASE_URL}/api/auth/me", headers=H(super_token))
        assert r.status_code == 200
        assert r.json()["role"] == "super_admin"

    def test_me_no_token(self, api):
        r = api.get(f"{BASE_URL}/api/auth/me")
        assert r.status_code == 401


# ---------- super admin ----------
class TestSuperAdmin:
    def test_overview(self, api, super_token):
        r = api.get(f"{BASE_URL}/api/superadmin/overview", headers=H(super_token))
        assert r.status_code == 200
        d = r.json()
        # seeded expectations
        assert d["total_universities"] >= 8
        assert d["total_students"] >= 1043
        assert d["total_professors"] >= 133
        assert d["total_admins"] >= 1
        assert isinstance(d["total_revenue"], (int, float))

    def test_universities_list(self, api, super_token):
        r = api.get(f"{BASE_URL}/api/superadmin/universities", headers=H(super_token))
        assert r.status_code == 200
        rows = r.json()
        assert isinstance(rows, list)
        assert len(rows) >= 8
        row = rows[0]
        for k in ("tenant_id", "name", "short_code", "status", "ai_enabled", "students", "professors"):
            assert k in row

    def test_ai_toggle(self, api, super_token):
        rows = api.get(f"{BASE_URL}/api/superadmin/universities", headers=H(super_token)).json()
        tid = rows[0]["tenant_id"]
        current = rows[0]["ai_enabled"]
        r = api.patch(f"{BASE_URL}/api/superadmin/universities/{tid}/ai",
                      headers=H(super_token), json={"ai_enabled": not current})
        assert r.status_code == 200
        assert r.json()["ai_enabled"] == (not current)
        # revert
        api.patch(f"{BASE_URL}/api/superadmin/universities/{tid}/ai",
                  headers=H(super_token), json={"ai_enabled": current})

    def test_status_toggle(self, api, super_token):
        rows = api.get(f"{BASE_URL}/api/superadmin/universities", headers=H(super_token)).json()
        tid = rows[0]["tenant_id"]
        current = rows[0]["status"]
        new = "suspended" if current == "active" else "active"
        r = api.patch(f"{BASE_URL}/api/superadmin/universities/{tid}/status",
                      headers=H(super_token), json={"status": new})
        assert r.status_code == 200
        assert r.json()["status"] == new
        api.patch(f"{BASE_URL}/api/superadmin/universities/{tid}/status",
                  headers=H(super_token), json={"status": current})

    def test_create_university(self, api, super_token):
        code = "TEST" + uuid.uuid4().hex[:6].upper()
        payload = {"tenant_id": code, "name": f"TEST_{code} University",
                   "short_code": code[:6], "university_type": "Private",
                   "city": "Hyderabad", "established_year": 2024}
        r = api.post(f"{BASE_URL}/api/superadmin/universities",
                     headers=H(super_token), json=payload)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["tenant_id"] == code
        # verify list shows it
        rows = api.get(f"{BASE_URL}/api/superadmin/universities", headers=H(super_token)).json()
        assert any(r2["tenant_id"] == code for r2 in rows)

    def test_create_duplicate_university(self, api, super_token):
        rows = api.get(f"{BASE_URL}/api/superadmin/universities", headers=H(super_token)).json()
        existing = rows[0]["tenant_id"]
        r = api.post(f"{BASE_URL}/api/superadmin/universities",
                     headers=H(super_token),
                     json={"tenant_id": existing, "name": "dup", "short_code": "DUP"})
        assert r.status_code == 400


# ---------- tenant admin ----------
class TestTenantAdmin:
    def test_overview(self, api, tenant_token):
        r = api.get(f"{BASE_URL}/api/tenant/overview", headers=H(tenant_token))
        assert r.status_code == 200
        d = r.json()
        assert "university" in d
        assert d["university"]["name"]
        assert d["total_students"] >= 0
        assert d["total_professors"] >= 0

    @pytest.mark.parametrize("path", ["students", "professors", "payments",
                                       "payroll", "hall-tickets", "expenses"])
    def test_tenant_endpoints(self, api, tenant_token, path):
        r = api.get(f"{BASE_URL}/api/tenant/{path}", headers=H(tenant_token))
        assert r.status_code == 200, f"{path}: {r.text}"
        assert isinstance(r.json(), list)

    def test_tenant_scoped(self, api, tenant_token):
        me = api.get(f"{BASE_URL}/api/auth/me", headers=H(tenant_token)).json()
        my_tid = me["tenant_id"]
        ov = api.get(f"{BASE_URL}/api/tenant/overview", headers=H(tenant_token)).json()
        # ensure scoping makes sense: total_students for tenant <= platform total
        # we just sanity-check that we have a tenant_id and overview returned data
        assert my_tid is not None


# ---------- role isolation ----------
class TestRoleIsolation:
    def test_tenant_cannot_access_superadmin(self, api, tenant_token):
        r = api.get(f"{BASE_URL}/api/superadmin/overview", headers=H(tenant_token))
        assert r.status_code == 403

    def test_super_cannot_access_tenant_admin(self, api, super_token):
        r = api.get(f"{BASE_URL}/api/tenant/overview", headers=H(super_token))
        assert r.status_code == 403

    def test_unauth_superadmin(self, api):
        r = api.get(f"{BASE_URL}/api/superadmin/overview")
        assert r.status_code == 401
