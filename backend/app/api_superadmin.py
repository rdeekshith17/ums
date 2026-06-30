"""Super Admin (platform operator) endpoints — manage all universities/tenants."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import require_role
from app.database import get_db
from app.models.finance import Payment
from app.models.university import University
from app.models.user import AdminProfile, ProfessorProfile, StudentProfile

router = APIRouter(prefix="/superadmin", tags=["superadmin"])
SUPER = require_role("super_admin")


@router.get("/overview")
def overview(db: Session = Depends(get_db), _=Depends(SUPER)):
    return {
        "total_universities": db.query(University).count(),
        "active": db.query(University).filter(University.status == "active").count(),
        "suspended": db.query(University).filter(University.status == "suspended").count(),
        "ai_enabled": db.query(University).filter(University.ai_enabled.is_(True)).count(),
        "total_students": db.query(StudentProfile).count(),
        "total_professors": db.query(ProfessorProfile).count(),
        "total_admins": db.query(AdminProfile).count(),
        "total_revenue": float(
            db.query(func.coalesce(func.sum(Payment.amount), 0))
            .filter(Payment.status == "success")
            .scalar()
        ),
    }


@router.get("/universities")
def list_universities(db: Session = Depends(get_db), _=Depends(SUPER)):
    sc = dict(
        db.query(StudentProfile.tenant_id, func.count(StudentProfile.id))
        .group_by(StudentProfile.tenant_id)
        .all()
    )
    pc = dict(
        db.query(ProfessorProfile.tenant_id, func.count(ProfessorProfile.id))
        .group_by(ProfessorProfile.tenant_id)
        .all()
    )
    out = []
    for u in db.query(University).order_by(University.name).all():
        out.append({
            "tenant_id": u.tenant_id,
            "name": u.name,
            "short_code": u.short_code,
            "university_type": u.university_type,
            "city": u.city,
            "established_year": u.established_year,
            "status": u.status,
            "ai_enabled": u.ai_enabled,
            "portal_url": u.portal_url,
            "students": sc.get(u.tenant_id, 0),
            "professors": pc.get(u.tenant_id, 0),
        })
    return out


class UniIn(BaseModel):
    tenant_id: str
    name: str
    short_code: str
    university_type: str = "State"
    city: str = "Hyderabad"
    established_year: int | None = None


@router.post("/universities")
def create_university(body: UniIn, db: Session = Depends(get_db), _=Depends(SUPER)):
    code = body.tenant_id.strip().upper()
    if db.query(University).filter(University.tenant_id == code).first():
        raise HTTPException(status_code=400, detail="A university with this code already exists")
    u = University(
        tenant_id=code, name=body.name, short_code=body.short_code,
        university_type=body.university_type, city=body.city, state="Telangana",
        established_year=body.established_year, ai_enabled=False, status="active",
        portal_url=f"https://{code.lower()}.uniai.app",
    )
    db.add(u)
    db.commit()
    return {"tenant_id": code, "name": u.name, "status": u.status}


class StatusIn(BaseModel):
    status: str  # active / suspended


@router.patch("/universities/{tenant_id}/status")
def set_status(tenant_id: str, body: StatusIn, db: Session = Depends(get_db), _=Depends(SUPER)):
    u = db.query(University).filter(University.tenant_id == tenant_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="University not found")
    if body.status not in ("active", "suspended"):
        raise HTTPException(status_code=400, detail="status must be active or suspended")
    u.status = body.status
    db.commit()
    return {"tenant_id": tenant_id, "status": u.status}


class AiIn(BaseModel):
    ai_enabled: bool


@router.patch("/universities/{tenant_id}/ai")
def set_ai(tenant_id: str, body: AiIn, db: Session = Depends(get_db), _=Depends(SUPER)):
    u = db.query(University).filter(University.tenant_id == tenant_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="University not found")
    u.ai_enabled = body.ai_enabled
    db.commit()
    return {"tenant_id": tenant_id, "ai_enabled": u.ai_enabled}
