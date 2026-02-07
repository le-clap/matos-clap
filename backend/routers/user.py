from fastapi import APIRouter, Depends, status
from sqlmodel import select, Session
from typing import List

from db.database import get_session
from models.models import User

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@router.get("/", response_model=List[User])
def get_user(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
        user: User,
        session: Session = Depends(get_session),
):

    session.add(user)
    session.commit()

    session.refresh(user)

    return user
