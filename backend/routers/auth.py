"""Authentication endpoints."""

from datetime import UTC, datetime, timedelta
from typing import Annotated
from urllib.parse import urlencode, urljoin

import structlog
from authlib.integrations.base_client import OAuthError
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlmodel import Session, select

from core.config import settings
from db.database import get_session
from models.enums import AccessLevel
from models.models import User, UserSession
from services.oidc import create_or_update_user, oauth

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
async def login(request: Request) -> RedirectResponse:
    return await oauth.cla.authorize_redirect(request, settings.CLA_REDIRECT_URI)


@router.get("/callback", status_code=status.HTTP_302_FOUND)
async def callback(request: Request, session: SessionDep) -> RedirectResponse:
    try:
        token = await oauth.cla.authorize_access_token(request)
    except OAuthError as e:
        logger.warning("auth.login_failed", error=e.error)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login failed") from e

    claims = dict(token["userinfo"])
    if "email" not in claims or "preferred_username" not in claims:
        claims |= await oauth.cla.userinfo(token=token)

    user = create_or_update_user(session, claims)
    user_session = _create_session(session, user)
    logger.info("auth.login", user_id=user.id, username=user.username)

    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    _set_session_cookie(response, user_session)
    return response


class LogoutResponse(BaseModel):
    logout_url: str | None


@router.post("/logout")
async def logout(
    session: SessionDep,
    response: Response,
    token: Annotated[str | None, Cookie(alias=settings.SESSION_COOKIE_NAME)] = None,
) -> LogoutResponse:
    logout_url = None
    if token:
        user_session = session.exec(select(UserSession).where(UserSession.token == token)).first()
        if user_session:
            logger.info("auth.logout", user_id=user_session.user_id)
            session.delete(user_session)
            session.commit()

            metadata = await oauth.cla.load_server_metadata()
            if endpoint := metadata.get("end_session_endpoint"):
                logout_url = f"{endpoint}?" + urlencode(
                    {
                        "client_id": settings.CLA_CLIENT_ID,
                        "post_logout_redirect_uri": urljoin(settings.CLA_REDIRECT_URI, "/"),
                    }
                )

    response.delete_cookie(key=settings.SESSION_COOKIE_NAME)
    return LogoutResponse(logout_url=logout_url)


if settings.ENABLE_DEV_LOGIN:

    @router.get("/dev-login", include_in_schema=False)
    def dev_login(session: SessionDep) -> RedirectResponse:
        user = session.exec(select(User)).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users in database")

        user.access_level = AccessLevel.ADMIN
        session.add(user)
        session.commit()
        session.refresh(user)

        logger.warning("auth.dev_login_used", user_id=user.id, username=user.username)
        user_session = _create_session(session, user)

        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        _set_session_cookie(response, user_session)
        return response
