"""
Shared audit log — owned by Team D (Infrastructure & QA).

This module defines the single `audit_logs` table and ONE helper, `log_event`,
that every other squad uses to record significant actions. Teams A and B import
`log_event` directly, so it is intentionally tiny and hard to misuse:

    from app.models.audit import log_event, EventType

    log_event(db, tenant_id, EventType.TENANT_CREATED, "Created via admin UI")

Do NOT construct AuditLog rows by hand elsewhere — always go through log_event
so writes stay consistent (commit handling, timestamps, validation) in one place.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import Session

from app.database import Base


def _utcnow() -> datetime:
    """Timezone-aware UTC now (avoids the deprecated naive datetime.utcnow)."""
    return datetime.now(timezone.utc)


class EventType:
    """
    Canonical event_type values. Import these constants instead of typing raw
    strings so typos can't silently create unqueryable audit rows.
    """

    TENANT_CREATED = "TENANT_CREATED"
    AI_ENABLED = "AI_ENABLED"
    AI_DISABLED = "AI_DISABLED"
    LAUNCH_REQUEST = "LAUNCH_REQUEST"

    #: Every value the audit log is allowed to store.
    ALL = frozenset(
        {TENANT_CREATED, AI_ENABLED, AI_DISABLED, LAUNCH_REQUEST}
    )


class AuditLog(Base):
    """ORM model for the shared `audit_logs` table."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    details = Column(Text, nullable=False, default="")
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    def __repr__(self) -> str:  # pragma: no cover - debug convenience only
        return (
            f"<AuditLog id={self.id} tenant_id={self.tenant_id!r} "
            f"event_type={self.event_type!r} created_at={self.created_at}>"
        )


def log_event(
    db: Session,
    tenant_id: str,
    event_type: str,
    details: str = "",
) -> AuditLog:
    """Create and commit a single audit-log row.

    This is the ONE entry point other squads should use to write to the audit
    log. It handles validation, timestamps, commit, and rollback so callers
    only need a single line.

    Args:
        db: An active SQLAlchemy ``Session`` (e.g. the request-scoped session
            injected via the ``get_db`` dependency).
        tenant_id: The tenant the event belongs to. Must be a non-empty string.
        event_type: One of the values in :class:`EventType` (TENANT_CREATED,
            AI_ENABLED, AI_DISABLED, LAUNCH_REQUEST). Pass the ``EventType``
            constant rather than a raw string to avoid typos.
        details: Optional free-form description or JSON string with extra
            context. Defaults to an empty string.

    Returns:
        The persisted :class:`AuditLog` row (with ``id`` and ``created_at``
        populated).

    Raises:
        ValueError: If ``tenant_id`` is empty or ``event_type`` is not a known
            :class:`EventType` value. This fails loudly so a bad call can never
            write a silently-corrupt audit row.

    Example:
        >>> from app.models.audit import log_event, EventType
        >>> log_event(db, tenant.tenant_id, EventType.AI_ENABLED, "Enabled by admin")
    """
    if not tenant_id or not isinstance(tenant_id, str):
        raise ValueError("log_event: tenant_id must be a non-empty string")

    if event_type not in EventType.ALL:
        raise ValueError(
            "log_event: event_type must be one of "
            f"{sorted(EventType.ALL)}, got {event_type!r}"
        )

    entry = AuditLog(
        tenant_id=tenant_id,
        event_type=event_type,
        details=details or "",
        created_at=_utcnow(),
    )

    db.add(entry)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(entry)
    return entry
