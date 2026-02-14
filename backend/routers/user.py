from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import select, Session
from typing import List

from db.database import get_session
from models.models import User, Access, Availability

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.get("/", response_model=List[User])
def get_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, session: Session = Depends(get_session)):
    return session.exec(select(User).where(User.id == user_id)).first()


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
        user: User,
        session: Session = Depends(get_session),
):
    if not session.get(Access, user.access_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Access ID {user.access_id} does not exist"
        )

    session.add(user)
    session.commit()

    session.refresh(user)

    return user
