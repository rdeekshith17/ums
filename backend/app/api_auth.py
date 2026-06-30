"""Auth endpoints: login + me."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, verify_password
from app.database import get_db
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginIn(BaseModel):
    email: str
    password: str


def user_out(u: User) -> dict:
    return {
        "id": u.id,
        "name": u.full_name,
        "email": u.email,
        "role": u.role,
        "tenant_id": u.tenant_id,
    }


@router.post("/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    email = body.email.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user or not user.password_hash or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    token = create_access_token(user)
    return {"access_token": token, "token_type": "bearer", "user": user_out(user)}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return user_out(user)
