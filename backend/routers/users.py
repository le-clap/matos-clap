"""User management endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlmodel import Session, select

from db.database import get_session
from dependencies.auth import get_current_user, require_role
from models.enums import AccessLevel
from models.models import User
from schemas.users import UserPatch, UserPublic

router = APIRouter(prefix="/users", tags=["users"])

# Dependency type aliases
SessionDep = Annotated[Session, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
ClapDep = Annotated[User, Depends(require_role(AccessLevel.CLAP))]
AdminDep = Annotated[User, Depends(require_role(AccessLevel.ADMIN))]


@router.get("/", response_model=list[UserPublic])
def get_users(session: SessionDep, _user: ClapDep) -> list[User]:
    return list(session.exec(select(User)).all())


@router.get("/me", response_model=UserPublic)
def get_me(user: CurrentUserDep) -> User:
    return user


@router.get(
    "/{user_id}",
    response_model=UserPublic,
    responses={404: {"description": "User not found"}},
)
def get_user_by_id(
    user_id: Annotated[int, Path(ge=1)],
    session: SessionDep,
    _user: ClapDep,
) -> User:
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
    user_id: Annotated[int, Path(ge=1)],
    user_patch: UserPatch,
    session: SessionDep,
    _user: AdminDep,
) -> User:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

    db_user.sqlmodel_update(user_patch.model_dump(exclude_unset=True))

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
