from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Cookie, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from core.config import settings
from db.database import get_session
from dependencies.auth import get_current_user
from models.enums import AccessLevel
from models.models import User, UserSession
from schemas.users import UserPublic
from services.cla_auth import create_or_update_user, get_auth_url, validate_ticket

router = APIRouter(prefix="/auth", tags=["auth"])


def _create_session(db: Session, user: User) -> UserSession:
    if user.id is None:
        raise ValueError("User must have an ID to create a session")

    user_session = UserSession(
        user_id=user.id,
        expires_at=datetime.now(UTC) + timedelta(days=settings.SESSION_TTL_DAYS),
    )
    db.add(user_session)
    db.commit()
    db.refresh(user_session)
    return user_session


def _set_session_cookie(response: RedirectResponse, user_session: UserSession) -> None:
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=user_session.token,
        httponly=True,
        samesite="lax",
        secure=settings.SESSION_COOKIE_SECURE,
        max_age=settings.SESSION_TTL_DAYS * 86400,
    )


@router.get("/login")
def cla_login():
    return RedirectResponse(url=get_auth_url())


@router.get("/cla/callback")
async def cla_callback(ticket: str, db: Session = Depends(get_session)):
    payload = await validate_ticket(ticket)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired ticket")

    user = create_or_update_user(db, payload)
    user_session = _create_session(db, user)

    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    _set_session_cookie(response, user_session)
    return response


@router.get("/me", response_model=UserPublic)
def get_me(user: User = Depends(get_current_user)):
    return user


@router.post("/logout")
def logout(
    db: Session = Depends(get_session),
    token: str | None = Cookie(None, alias=settings.SESSION_COOKIE_NAME),
):
    if token:
        user_session = db.exec(select(UserSession).where(UserSession.token == token)).first()
        if user_session:
            db.delete(user_session)
            db.commit()

    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key=settings.SESSION_COOKIE_NAME)
    return response


if settings.DEBUG:

    @router.get("/dev/login")
    def dev_login(db: Session = Depends(get_session)):
        user = db.exec(select(User)).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users in database")

        user.access_level = AccessLevel.ADMIN
        db.add(user)
        db.commit()
        db.refresh(user)

        user_session = _create_session(db, user)

        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        _set_session_cookie(response, user_session)
        return response
