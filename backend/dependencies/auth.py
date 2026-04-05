from datetime import UTC, datetime

from fastapi import Cookie, Depends, Header, HTTPException, status
from sqlmodel import Session, select

from core.config import settings
from db.database import get_session
from models.enums import AccessLevel
from models.models import User, UserSession


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


def _get_user_from_token(session: Session, token: str | None, *, optional: bool) -> User | None:
    if not token:
        if optional:
            return None
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user_session = session.exec(select(UserSession).where(UserSession.token == token)).first()
    if not user_session:
        if optional:
            return None
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    if user_session.expires_at < datetime.now(UTC):
        session.delete(user_session)
        session.commit()
        if optional:
            return None
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    return user_session.user


def get_current_user(
    session: Session = Depends(get_session),
    cookie_token: str | None = Cookie(None, alias=settings.SESSION_COOKIE_NAME),
    authorization: str | None = Header(None),
) -> User:
    token = _resolve_session_token(cookie_token, authorization)
    user = _get_user_from_token(session, token, optional=False)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


def get_current_user_optional(
    session: Session = Depends(get_session),
    cookie_token: str | None = Cookie(None, alias=settings.SESSION_COOKIE_NAME),
    authorization: str | None = Header(None),
) -> User | None:
    token = _resolve_session_token(cookie_token, authorization)
    return _get_user_from_token(session, token, optional=True)


def require_role(min_level: AccessLevel):
    level_order = list(AccessLevel)

    def dependency(user: User = Depends(get_current_user)) -> User:
        if level_order.index(user.access_level) < level_order.index(min_level):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return dependency


def has_role(user: User, min_level: AccessLevel) -> bool:
    level_order = list(AccessLevel)
    return level_order.index(user.access_level) >= level_order.index(min_level)
