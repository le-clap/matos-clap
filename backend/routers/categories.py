"""Category management endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from db.database import get_session
from dependencies.auth import get_current_user, require_role
from models.enums import AccessLevel
from models.models import Category, User
from schemas.categories import CategoryPatch, CategoryPost, CategoryPublic

router = APIRouter(prefix="/categories", tags=["categories"])

# Dependency type aliases
SessionDep = Annotated[Session, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
ManagerDep = Annotated[User, Depends(require_role(AccessLevel.MANAGER))]


@router.get("/", response_model=list[CategoryPublic])
def get_categories(session: SessionDep, _user: CurrentUserDep) -> list[Category]:
    return list(session.exec(select(Category)).all())


@router.get(
    "/{category_id}",
    response_model=CategoryPublic,
    responses={404: {"description": "Category not found"}},
)
def get_category_by_id(
    session: SessionDep,
    _user: CurrentUserDep,
    category_id: Annotated[int, Path(ge=1)],
) -> Category:
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with ID {category_id} not found")
    return category


@router.post("/", response_model=CategoryPublic, status_code=status.HTTP_201_CREATED)
def create_category(
    session: SessionDep,
    _user: ManagerDep,
    category: CategoryPost,
) -> Category:
    db_category = Category(**category.model_dump())
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@router.patch(
    "/{category_id}",
    response_model=CategoryPublic,
    responses={404: {"description": "Category not found"}},
)
def update_category(
    session: SessionDep,
    _user: ManagerDep,
    category_id: Annotated[int, Path(ge=1)],
    category_patch: CategoryPatch,
) -> Category:
    db_category = session.get(Category, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail=f"Category with ID {category_id} not found")

    db_category.sqlmodel_update(category_patch.model_dump(exclude_unset=True))
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "Category not found"},
        409: {"description": "Category still used by catalogs"},
    },
)
def delete_category(
    session: SessionDep,
    _user: ManagerDep,
    category_id: Annotated[int, Path(ge=1)],
) -> None:
    db_category = session.get(Category, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail=f"Category with ID {category_id} not found")

    try:
        session.delete(db_category)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete category: still used by catalogs",
        ) from e
