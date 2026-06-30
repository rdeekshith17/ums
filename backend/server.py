"""UniAI backend — FastAPI app wired to PostgreSQL (SQLAlchemy)."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

import app.models  # noqa: F401,E402  (register all models)
from app.api_auth import router as auth_router  # noqa: E402
from app.api_superadmin import router as superadmin_router  # noqa: E402
from app.api_tenant import router as tenant_router  # noqa: E402

app = FastAPI(title="UniAI — University AI Dashboard")

app.include_router(auth_router, prefix="/api")
app.include_router(superadmin_router, prefix="/api")
app.include_router(tenant_router, prefix="/api")


@app.get("/api/")
def root():
    return {"message": "UniAI API is running"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
