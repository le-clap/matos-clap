"""OIDC client for the CLA identity provider (authorization code flow + PKCE)."""

from authlib.integrations.starlette_client import OAuth
from sqlmodel import Session, select

from core.config import settings
from models.models import User

oauth = OAuth()
oauth.register(
    name="cla",
    server_metadata_url=f"{settings.CLA_ISSUER}/.well-known/openid-configuration",
    client_id=settings.CLA_CLIENT_ID,
    client_secret=settings.CLA_CLIENT_SECRET,
    client_kwargs={"scope": "openid profile email", "code_challenge_method": "S256"},
)


def create_or_update_user(session: Session, claims: dict) -> User:
    """Match on preferred_username and refresh name/email from the IdP."""
    username = claims["preferred_username"]
    name = claims.get("name") or username

    user = session.exec(select(User).where(User.username == username)).first()
    if user:
        user.email = claims["email"]
        user.name = name
    else:
        user = User(username=username, name=name, email=claims["email"])
        session.add(user)

    session.commit()
    session.refresh(user)
    return user
