from datetime import UTC, datetime

import structlog
from fastapi import Cookie, Depends, Header, HTTPException, status
from sqlmodel import Session, select

from core.config import settings
from db.database import get_session
from models.enums import AccessLevel
from models.models import User, UserSession

logger = structlog.get_logger(__name__)


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token


def _resolve_session_token(cookie_token: str | None, authorization: str | None) -> str | None:
    bearer_token = _extract_bearer_token(authorization)
    return bearer_token or cookie_token


def _get_user_from_token(session: Session, token: str | None) -> User:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user_session = session.exec(select(UserSession).where(UserSession.token == token)).first()
    if not user_session:
        logger.warning("auth.invalid_session", token_suffix=token[-6:])
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    expires_at = user_session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if expires_at < datetime.now(UTC):
        session.delete(user_session)
        session.commit()
        logger.warning("auth.session_expired", user_id=user_session.user_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    return user_session.user


async def get_current_user(
    session: Session = Depends(get_session),
    cookie_token: str | None = Cookie(None, alias=settings.SESSION_COOKIE_NAME),
    authorization: str | None = Header(None),
) -> User:
    """Get the current authenticated user. Needs to be async to write to contextvars."""
    token = _resolve_session_token(cookie_token, authorization)
    user = _get_user_from_token(session, token)
    structlog.contextvars.bind_contextvars(user_id=user.id, username=user.username)
    return user


def require_role(min_level: AccessLevel):
    level_order = list(AccessLevel)

    def dependency(user: User = Depends(get_current_user)) -> User:
        if level_order.index(user.access_level) < level_order.index(min_level):
            logger.warning("auth.permission_denied", required=min_level, actual=user.access_level)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return dependency


def has_role(user: User, min_level: AccessLevel) -> bool:
    level_order = list(AccessLevel)
    return level_order.index(user.access_level) >= level_order.index(min_level)
