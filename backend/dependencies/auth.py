from datetime import UTC, datetime

from fastapi import Cookie, Depends, HTTPException, status
from sqlmodel import Session, select

from core.config import settings
from db.database import get_session
from models.enums import AccessLevel
from models.models import User, UserSession


def get_current_user(
    session: Session = Depends(get_session),
    token: str | None = Cookie(None, alias=settings.SESSION_COOKIE_NAME),
) -> User:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user_session = session.exec(select(UserSession).where(UserSession.token == token)).first()
    if not user_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    if user_session.expires_at < datetime.now(UTC):
        session.delete(user_session)
        session.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    return user_session.user


def get_current_user_optional(
    session: Session = Depends(get_session),
    token: str | None = Cookie(None, alias=settings.SESSION_COOKIE_NAME),
) -> User | None:
    if not token:
        return None

    user_session = session.exec(select(UserSession).where(UserSession.token == token)).first()
    if not user_session or user_session.expires_at < datetime.now(UTC):
        return None

    return user_session.user


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
