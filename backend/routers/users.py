"""User management endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import func
from sqlmodel import Session, select

from db.database import get_session
from dependencies.auth import get_current_user, require_role
from models.enums import AccessLevel
from models.models import User
from schemas.users import UserPatch, UserPublic
from schemas.utils import PaginatedResponse, PaginationParams

router = APIRouter(prefix="/users", tags=["users"])

# Dependency type aliases
SessionDep = Annotated[Session, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
ClapDep = Annotated[User, Depends(require_role(AccessLevel.CLAP))]
AdminDep = Annotated[User, Depends(require_role(AccessLevel.ADMIN))]


@router.get("/", response_model=PaginatedResponse[UserPublic])
def get_users(
    session: SessionDep,
    _user: ClapDep,
    pagination: Annotated[PaginationParams, Depends()],
    access_level: AccessLevel | None = None,
) -> PaginatedResponse[User]:
    base_statement = select(User)

    if access_level is not None:
        base_statement = base_statement.where(User.access_level == access_level)

    total = session.exec(select(func.count()).select_from(base_statement.subquery())).one()

    statement = base_statement.offset(pagination.offset()).limit(pagination.limit)
    users = session.exec(statement).all()

    return PaginatedResponse(
        items=list(users),
        total=total,
        limit=pagination.limit,
        page=pagination.page,
        search=pagination.search,
    )


@router.get("/me", response_model=UserPublic)
def get_me(user: CurrentUserDep) -> User:
    return user


@router.get(
    "/{user_id}",
    response_model=UserPublic,
    responses={404: {"description": "User not found"}},
)
def get_user_by_id(
    session: SessionDep,
    _user: ClapDep,
    user_id: Annotated[int, Path(ge=1)],
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
    session: SessionDep,
    _user: AdminDep,
    user_id: Annotated[int, Path(ge=1)],
    user_patch: UserPatch,
) -> User:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

    db_user.sqlmodel_update(user_patch.model_dump(exclude_unset=True))

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
