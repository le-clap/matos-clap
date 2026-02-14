from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import select, Session
from typing import List

from db.database import get_session
from models.models import Item, Catalog, Condition, Availability

router = APIRouter(
    prefix="/item",
    tags=["item"],
)

@router.get("/", response_model=List[Item])
def get_items(session: Session = Depends(get_session)):
    return session.exec(select(Item)).all()

@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(item: Item, session: Session = Depends(get_session)):
    if not session.get(Catalog, item.catalog_id):
        raise HTTPException(
            status_code=404,
            detail=f"Catalog entry with id {item.catalog_id} not found"
        )

    if not session.get(Condition, item.condition_id):
        raise HTTPException(
            status_code=404,
            detail=f"Condition id {item.condition_id} not found"
        )

    if not session.get(Availability, item.availability_id):
        raise HTTPException(
            status_code=404,
            detail=f"Availability id {item.availability_id} not found"
        )

    # 2. Add the item to the session
    session.add(item)

    # 3. Commit to save it to db.db
    session.commit()

    # 4. Refresh to get the auto-generated ID back from the DB
    session.refresh(item)

    return item

@router.delete("/item/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, session: Session = Depends(get_session)):
    # 1. Fetch the object
    item = session.get(Item, item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # 2. Delete it
    session.delete(item)

    # 3. Commit
    session.commit()

    # 4. Return nothing (Standard for 204 No Content)
    return None

@router.delete("/{item_id}/soft-delete", response_model=Item)
def soft_delete_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.deleted = True
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@router.delete("/{item_id}/soft-undelete", response_model=Item)
def soft_undelete_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.deleted = False
    session.add(item)
    session.commit()
    session.refresh(item)
    return item