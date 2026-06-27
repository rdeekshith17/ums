"""
Health checks — owned by Team D (Infrastructure & QA).

Two endpoints so Docker/K8s probes and anyone debugging a deployment can quickly
tell *what* is broken:

    GET /health      -> app process is up (no dependencies touched)
    GET /health/db   -> app can actually reach the database

Liveness probes should point at /health; readiness probes at /health/db.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    """Liveness check — confirms the app process is running.

    Intentionally has no dependencies (no DB, no external calls) so it stays
    fast and never fails for reasons outside the app process itself.
    """
    return {"status": "ok"}


@router.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    """Readiness check — confirms the app can reach the database.

    Runs a trivial ``SELECT 1``. Returns ``{"status": "ok"}`` on success, or a
    500 with a clear error message if the database is unreachable.
    """
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Database health check failed: {exc}",
        )
    return {"status": "ok"}
