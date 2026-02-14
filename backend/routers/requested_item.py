from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import select, Session
from typing import List

from db.database import get_session
from models.models import RequestedItem, Request, Catalog

router = APIRouter(
    prefix="/requested-item",
    tags=["requested-item"],
)

@router.get("/", response_model=List[RequestedItem])
def get_requested_items(session: Session = Depends(get_session)):
    return session.exec(select(RequestedItem)).all()

@router.post("/", response_model=RequestedItem, status_code=status.HTTP_201_CREATED)
def create_user(
        requested_item: RequestedItem,
        session: Session = Depends(get_session),
):

    if not session.get(Request, requested_item.request_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request ID {requested_item.request_id} does not exist")

    if not session.get(Catalog, requested_item.catalog_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catalog ID {requested_item.catalog_id} does not exist")

    session.add(requested_item)
    session.commit()

    session.refresh(requested_item)

    return requested_item
