from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from db.database import get_session
from models.models import Catalog, Request, RequestedCatalog

router = APIRouter(
    prefix="/requested-catalogs",
    tags=["requested-catalog"],
)


@router.get("/", response_model=list[RequestedCatalog])
def get_requested_catalogs(session: Session = Depends(get_session)):
    return session.exec(select(RequestedCatalog)).all()


@router.post("/", response_model=RequestedCatalog, status_code=status.HTTP_201_CREATED)
def create_user(
    requested_catalog: RequestedCatalog,
    session: Session = Depends(get_session),
):
    if not session.get(Request, requested_catalog.request_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Request ID {requested_catalog.request_id} does not exist"
        )

    if not session.get(Catalog, requested_catalog.catalog_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Catalog ID {requested_catalog.catalog_id} does not exist"
        )

    session.add(requested_catalog)
    session.commit()

    session.refresh(requested_catalog)

    return requested_catalog
