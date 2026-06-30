# UniAI — Local Development Guide (VS Code)

Run the full UniAI app (React + FastAPI + database) on your own machine in VS Code.

---

## 1. Prerequisites

Install these first:

| Tool | Version | Check |
|---|---|---|
| **Python** | 3.10 – 3.12 | `python --version` |
| **Node.js** | 18 or 20 LTS | `node --version` |
| **Yarn** | 1.22+ | `yarn --version` (install: `npm i -g yarn`) |
| **Git** | any | `git --version` |
| **VS Code** | latest | — |
| **PostgreSQL** *(optional)* | 14+ | only for the "production-like" DB option |

**Recommended VS Code extensions:**
- Python (`ms-python.python`) + Pylance
- ESLint (`dbaeumer.vscode-eslint`)
- Tailwind CSS IntelliSense (`bradlc.vscode-tailwindcss`)
- SQLite Viewer (`qwtel.sqlite-viewer`) — to browse the dev DB

---

## 2. Project Structure

```
project-root/
├── backend/                 # FastAPI + SQLAlchemy
│   ├── app/                 # models, auth, API routers
│   │   ├── api_auth.py      # /api/auth/login, /me, /logout
│   │   ├── api_superadmin.py
│   │   ├── api_tenant.py
│   │   ├── auth.py          # JWT + role guards
│   │   ├── database.py      # engine/session (reads DATABASE_URL)
│   │   └── models/          # 17 ORM tables
│   ├── server.py            # FastAPI app entrypoint (uvicorn server:app)
│   ├── seed_data.py         # generates the Telangana sample data
│   ├── auth_seed.py         # creates login accounts
│   ├── requirements.txt
│   └── .env
└── frontend/                # React (CRA + craco + Tailwind)
    ├── src/
    ├── package.json
    └── .env
```

---

## 3. Open in VS Code

```bash
cd project-root
code .
```
Use **Terminal → New Terminal** and split it into two (one for backend, one for frontend).

---

## 4. Backend Setup (FastAPI)

In **Terminal 1**:

```bash
cd backend

# 1) create & activate a virtual environment
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows (PowerShell):
# .venv\Scripts\Activate.ps1

# 2) install dependencies
pip install -r requirements.txt
# if sqlalchemy / psycopg2 are missing:
pip install sqlalchemy psycopg2-binary bcrypt pyjwt python-dotenv

# 3) create the backend/.env file (see section 6)

# 4) build the database + sample data + login accounts
python seed_data.py     # creates uniai_dev.db with all sample data
python auth_seed.py      # creates super_admin + sets tenant-admin passwords

# 5) run the API (hot reload)
uvicorn server:app --reload --port 8001
```

Backend is now at **http://localhost:8001**. Test it:
```bash
curl http://localhost:8001/api/
# {"message":"UniAI API is running"}
```
Interactive API docs: **http://localhost:8001/docs**

---

## 5. Frontend Setup (React)

In **Terminal 2**:

```bash
cd frontend

# 1) install dependencies (use yarn, not npm)
yarn install

# 2) create frontend/.env (see section 6)

# 3) start the dev server
yarn start
```

Frontend opens at **http://localhost:3000**.

---

## 6. Environment Files (IMPORTANT for local)

### `backend/.env`
```
DATABASE_URL="sqlite:///./uniai_dev.db"
JWT_SECRET="change-me-to-a-long-random-hex-string"
CORS_ORIGINS="http://localhost:3000"
COOKIE_SECURE="false"
COOKIE_SAMESITE="lax"
```

> **Why `COOKIE_SECURE=false` / `COOKIE_SAMESITE=lax` locally?**
> The login cookie is normally `Secure; SameSite=None` (required for the hosted
> https preview). Browsers **reject `Secure` cookies over `http://localhost`**,
> which would break login/logout locally. Setting these two vars makes the cookie
> work over plain http. **On a real https server, set them back to
> `true` / `none`.**

### `frontend/.env`
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

> Restart `yarn start` after editing `frontend/.env` (CRA only reads it at boot).

---

## 7. Log In

Open **http://localhost:3000** → use the demo accounts (also shown on the login page):

| Role | Email | Password |
|---|---|---|
| **Super Admin** | `superadmin@uniai.app` | `SuperAdmin@123` |
| **Tenant Admin** | `aishwarya.mudirajadm4@ku.ac.in` | `Admin@123` |

(Any university admin email from `backend/seed_output/admins.csv` works with `Admin@123`.)

---

## 8. Database Options

### Option A — SQLite (default, zero setup)
Already configured above. The file `backend/uniai_dev.db` holds everything.
Browse it in VS Code with the **SQLite Viewer** extension.

### Option B — PostgreSQL (production-like)
1. Create a database:
   ```bash
   createdb uniai
   ```
2. Point the backend at it in `backend/.env`:
   ```
   DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/uniai"
   ```
3. Load data — either re-run the seeders (identical data, native PG types):
   ```bash
   python seed_data.py && python auth_seed.py
   ```
   …or import the provided dump:
   ```bash
   pg_restore --no-owner --no-privileges -d uniai backend/backups/uniai_postgres.dump
   ```

---

## 9. VS Code Run/Debug (optional)

Create **`.vscode/launch.json`** to debug the backend with breakpoints:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI: backend",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": ["server:app", "--reload", "--port", "8001"],
      "cwd": "${workspaceFolder}/backend",
      "envFile": "${workspaceFolder}/backend/.env",
      "justMyCode": true
    }
  ]
}
```

Then press **F5** to run the API with the debugger. Run the frontend separately with `yarn start`.

---

## 10. Daily Workflow

| Action | Command |
|---|---|
| Start backend | `cd backend && source .venv/bin/activate && uvicorn server:app --reload --port 8001` |
| Start frontend | `cd frontend && yarn start` |
| Reset/regenerate sample data | `cd backend && python seed_data.py && python auth_seed.py` |
| Backend API docs | http://localhost:8001/docs |
| App | http://localhost:3000 |

Both servers hot-reload on file changes — no restart needed except for `.env` edits.

---

## 11. Troubleshooting

| Symptom | Fix |
|---|---|
| **Login works but logout/refresh keeps you logged in** | Set `COOKIE_SECURE=false` and `COOKIE_SAMESITE=lax` in `backend/.env`, restart backend, clear cookies once. |
| **CORS error in browser console** | `CORS_ORIGINS` in `backend/.env` must exactly equal your frontend origin (`http://localhost:3000`). Restart backend. |
| **401 on every request** | Cookie not being sent — confirm `frontend/src/lib/api.js` uses `withCredentials: true` and `REACT_APP_BACKEND_URL=http://localhost:8001`. |
| **`ModuleNotFoundError: app`** | Run uvicorn **from the `backend/` folder** so `server:app` and the `app` package resolve. |
| **`psycopg2` build error** | Use `psycopg2-binary` (already in the instructions). |
| **Frontend env not applied** | Stop and re-run `yarn start` after editing `frontend/.env`. |
| **Port already in use** | Change `--port` (backend) or set `PORT=3001 yarn start` (frontend) + update `REACT_APP_BACKEND_URL`. |

---

## 12. Production Notes
- Use **PostgreSQL** (Option B), not SQLite.
- Serve over **HTTPS** and set `COOKIE_SECURE=true`, `COOKIE_SAMESITE=none`.
- Set a strong random `JWT_SECRET`.
- Set `CORS_ORIGINS` to your real frontend domain.
- Build the frontend with `yarn build` and serve the static files behind your web server / CDN.
