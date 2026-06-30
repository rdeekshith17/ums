"""Auth endpoints: login + me."""

from datetime import datetime, timezone
import os

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import (
    ACCESS_TOKEN_MINUTES,
    create_access_token,
    get_current_user,
    verify_password,
)
from app.database import get_db
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_NAME = "access_token"
# Configurable so local http://localhost dev works (Secure cookies need https).
# Production/preview (https): COOKIE_SECURE=true, COOKIE_SAMESITE=none
# Local dev   (http):         COOKIE_SECURE=false, COOKIE_SAMESITE=lax
COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "true").lower() == "true"
COOKIE_SAMESITE = os.environ.get("COOKIE_SAMESITE", "none")


def _set_auth_cookie(response: Response, token: str, max_age: int) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=max_age,
        path="/",
    )


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
def login(body: LoginIn, response: Response, db: Session = Depends(get_db)):
    email = body.email.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user or not user.password_hash or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    token = create_access_token(user)
    _set_auth_cookie(response, token, ACCESS_TOKEN_MINUTES * 60)
    # token also returned for non-browser/API clients; browsers use the httpOnly cookie.
    return {"access_token": token, "token_type": "bearer", "user": user_out(user)}


@router.post("/logout")
def logout(response: Response):
    # Overwrite with identical attributes + immediate expiry so the browser
    # actually clears the session cookie.
    _set_auth_cookie(response, "", 0)
    return {"ok": True}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return user_out(user)
