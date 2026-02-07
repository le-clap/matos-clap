from fastapi import APIRouter, Depends, status
from sqlmodel import select, Session
from typing import List

from db.database import get_session
from models.models import Catalog

router = APIRouter(
    prefix="/catalog",
    tags=["catalog"],
)

@router.get("/", response_model=List[Catalog])
def get_catalogs(session: Session = Depends(get_session)):
    return session.exec(select(Catalog)).all()

@router.post("/", response_model=Catalog, status_code=status.HTTP_201_CREATED)
def create_catalog_entry(
        catalog_entry: Catalog,
        session: Session = Depends(get_session),
):
    if not session.get(Category, catalog_entry.category_id):
        raise HTTPException(
            status_code=404,
            detail=f"Category {catalog_entry.category_id} not found"
        )

    session.add(catalog_entry)
    session.commit()

    session.refresh(catalog_entry)

    return catalog_entry