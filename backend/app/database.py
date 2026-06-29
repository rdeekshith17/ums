"""
Database foundation — owned by Team D (Infrastructure & QA).

Defines the SQLAlchemy engine, session factory, declarative Base, and the
`get_db` dependency that every route/service uses for a request-scoped session.

DATABASE_URL is read from the environment. For local dev it falls back to a
SQLite file so the project runs without a Postgres server; in staging/production
set DATABASE_URL to the Postgres connection string.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./uniai_dev.db")

# SQLite needs this flag when used across threads (dev only).
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a request-scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
