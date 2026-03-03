from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db.database import get_session
from dependencies.auth import get_current_user, require_role
from models.enums import AccessLevel
from models.models import User
from schemas.users import UserPatch, UserPublic

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/", response_model=list[UserPublic])
def get_users(session: Session = Depends(get_session), _user=Depends(require_role(AccessLevel.CLAP))):
    return session.exec(select(User)).all()


@router.get("/me", response_model=UserPublic)
def get_me(user: User = Depends(get_current_user)):
    return user


@router.get(
    "/{user_id}",
    response_model=UserPublic,
    responses={404: {"description": "User not found"}},
)
def get_user_by_id(
    user_id: int, session: Session = Depends(get_session), _user=Depends(require_role(AccessLevel.CLAP))
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
    return user


@router.patch(
    "/{user_id}",
    response_model=UserPublic,
    responses={404: {"description": "User not found"}},
)
def update_user(
    user_id: int,
    user_patch: UserPatch,
    session: Session = Depends(get_session),
    _user=Depends(require_role(AccessLevel.ADMIN)),
):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

    db_user.sqlmodel_update(user_patch.model_dump(exclude_unset=True))

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
