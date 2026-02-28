import httpx
from sqlmodel import select

from core.config import settings
from models.models import User


def get_auth_url() -> str:
    return f"{settings.CLA_HOST}/authentification/{settings.CLA_IDENTIFIER}"


async def validate_ticket(ticket: str) -> dict | None:
    url = f"{settings.CLA_HOST}/authentification/{settings.CLA_IDENTIFIER}/{ticket}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        if response.status_code != 200:
            return None

        data = response.json()
        return data["payload"] if data.get("success") else None
    except Exception:
        return None


def create_or_update_user(session, cla_data: dict) -> User:
    user = session.exec(select(User).where(User.username == cla_data["username"])).first()

    if user:
        user.email = cla_data["emailSchool"]
        user.name = f"{cla_data['firstName']} {cla_data['lastName']}"
    else:
        user = User(
            username=cla_data["username"],
            name=f"{cla_data['firstName']} {cla_data['lastName']}",
            email=cla_data["emailSchool"],
        )
        session.add(user)

    session.commit()
    session.refresh(user)
    return user
