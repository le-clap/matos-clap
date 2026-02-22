from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from db.database import get_session
from models.models import Catalog, Category
from schemas.catalog import CatalogPatch, CatalogPost, CatalogPublic

router = APIRouter(
    prefix="/catalogs",
    tags=["catalog"],
)


@router.get("/", response_model=list[CatalogPublic])
def get_catalogs(session: Session = Depends(get_session)):
    statement = select(Catalog).options(joinedload(Catalog.category))  # ty: ignore[invalid-argument-type]
    return session.exec(statement).all()


@router.get(
    "/{catalog_id}",
    response_model=CatalogPublic,
    responses={404: {"description": "Catalog not found"}},
)
def get_catalog_by_id(catalog_id: int, session: Session = Depends(get_session)):
    statement = (
        select(Catalog).where(Catalog.id == catalog_id).options(joinedload(Catalog.category))
    )  # ty: ignore[invalid-argument-type]
    catalog = session.exec(statement).first()
    if not catalog:
        raise HTTPException(status_code=404, detail=f"Catalog with ID {catalog_id} not found")
    return catalog


@router.post(
    "/",
    response_model=CatalogPublic,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"description": "Category not found"}},
)
def create_catalog(catalog: CatalogPost, session: Session = Depends(get_session)):
    if not session.get(Category, catalog.category_id):
        raise HTTPException(status_code=404, detail=f"Category with ID {catalog.category_id} not found")

    db_catalog = Catalog(**catalog.model_dump())
    session.add(db_catalog)
    session.commit()
    session.refresh(db_catalog)
    return db_catalog


@router.patch(
    "/{catalog_id}",
    response_model=CatalogPublic,
    responses={404: {"description": "Catalog or referenced category not found"}},
)
def update_catalog(
    catalog_id: int,
    catalog_patch: CatalogPatch,
    session: Session = Depends(get_session),
):
    db_catalog = session.get(Catalog, catalog_id)
    if not db_catalog:
        raise HTTPException(status_code=404, detail=f"Catalog with ID {catalog_id} not found")

    update_data = catalog_patch.model_dump(exclude_unset=True)

    if "category_id" in update_data and not session.get(Category, update_data["category_id"]):
        raise HTTPException(status_code=404, detail=f"Category with ID {update_data['category_id']} not found")

    db_catalog.sqlmodel_update(update_data)
    session.add(db_catalog)
    session.commit()
    session.refresh(db_catalog)
    return db_catalog


@router.delete(
    "/{catalog_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "Catalog not found"},
        409: {"description": "Catalog still used by items or requests"},
    },
)
def delete_catalog(catalog_id: int, session: Session = Depends(get_session)):
    db_catalog = session.get(Catalog, catalog_id)
    if not db_catalog:
        raise HTTPException(status_code=404, detail=f"Catalog with ID {catalog_id} not found")

    try:
        session.delete(db_catalog)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete catalog: still used by items or requests",
        ) from e
