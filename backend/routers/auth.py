"""Authentication endpoints."""

from datetime import UTC, datetime, timedelta
from typing import Annotated

import structlog
from fastapi import APIRouter, Cookie, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from core.config import settings
from db.database import get_session
from models.enums import AccessLevel
from models.models import User, UserSession
from services.cla_auth import create_or_update_user, get_auth_url, validate_ticket

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

# Dependency type aliases
SessionDep = Annotated[Session, Depends(get_session)]


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
def cla_login() -> RedirectResponse:
    return RedirectResponse(url=get_auth_url())


@router.get("/cla/callback", status_code=status.HTTP_302_FOUND)
async def cla_callback(ticket: str, db: SessionDep) -> RedirectResponse:
    payload = await validate_ticket(ticket)
    if not payload:
        logger.warning("auth.login_failed")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired ticket")

    user = create_or_update_user(db, payload)
    user_session = _create_session(db, user)
    logger.info("auth.login", user_id=user.id, username=user.username)

    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    _set_session_cookie(response, user_session)
    return response


@router.post("/logout", status_code=status.HTTP_302_FOUND)
def logout(
    db: SessionDep,
    token: Annotated[str | None, Cookie(alias=settings.SESSION_COOKIE_NAME)] = None,
) -> RedirectResponse:
    if token:
        user_session = db.exec(select(UserSession).where(UserSession.token == token)).first()
        if user_session:
            logger.info("auth.logout", user_id=user_session.user_id)
            db.delete(user_session)
            db.commit()

    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key=settings.SESSION_COOKIE_NAME)
    return response


if settings.ENABLE_DEV_LOGIN:

    @router.get("/dev-login", include_in_schema=False)
    def dev_login(db: SessionDep) -> RedirectResponse:
        user = db.exec(select(User)).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users in database")

        user.access_level = AccessLevel.ADMIN
        db.add(user)
        db.commit()
        db.refresh(user)

        logger.warning("auth.dev_login_used", user_id=user.id, username=user.username)
        user_session = _create_session(db, user)

        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        _set_session_cookie(response, user_session)
        return response
