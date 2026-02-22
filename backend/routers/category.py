from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from db.database import get_session
from models.models import Category
from schemas.category import CategoryPatch, CategoryPost, CategoryPublic

router = APIRouter(
    prefix="/categories",
    tags=["category"],
)


@router.get("/", response_model=list[CategoryPublic])
def get_categories(session: Session = Depends(get_session)):
    return session.exec(select(Category)).all()


@router.get(
    "/{category_id}",
    response_model=CategoryPublic,
    responses={404: {"description": "Category not found"}},
)
def get_category_by_id(category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with ID {category_id} not found")
    return category


@router.post("/", response_model=CategoryPublic, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryPost, session: Session = Depends(get_session)):
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
    category_id: int,
    category_patch: CategoryPatch,
    session: Session = Depends(get_session),
):
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
def delete_category(category_id: int, session: Session = Depends(get_session)):
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
