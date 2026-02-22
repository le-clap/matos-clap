from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from db.database import get_session
from models.models import Availability, Catalog, Condition, Item
from schemas.item import ItemPatch, ItemPost, ItemPublic

router = APIRouter(
    prefix="/items",
    tags=["item"],
)


def _validate_item_refs(
    session: Session,
    catalog_id: int | None,
    condition_id: int | None,
    availability_id: int | None,
):
    if catalog_id is not None and not session.get(Catalog, catalog_id):
        raise HTTPException(status_code=404, detail=f"Catalog with ID {catalog_id} not found")
    if condition_id is not None and not session.get(Condition, condition_id):
        raise HTTPException(status_code=404, detail=f"Condition with ID {condition_id} not found")
    if availability_id is not None and not session.get(Availability, availability_id):
        raise HTTPException(status_code=404, detail=f"Availability with ID {availability_id} not found")


def _item_load_options():
    return [
        joinedload(Item.catalog).joinedload(Catalog.category),  # ty: ignore[invalid-argument-type]
        joinedload(Item.condition),  # ty: ignore[invalid-argument-type]
        joinedload(Item.availability),  # ty: ignore[invalid-argument-type]
    ]


@router.get("/", response_model=list[ItemPublic])
def get_items(include_deleted: bool = False, session: Session = Depends(get_session)):
    statement = select(Item).options(*_item_load_options())
    if not include_deleted:
        statement = statement.where(Item.deleted == False)  # noqa: E712
    return session.exec(statement).unique().all()


@router.get(
    "/{item_id}",
    response_model=ItemPublic,
    responses={404: {"description": "Item not found"}},
)
def get_item_by_id(item_id: int, session: Session = Depends(get_session)):
    statement = select(Item).where(Item.id == item_id).options(*_item_load_options())
    item = session.exec(statement).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")
    return item


@router.post(
    "/",
    response_model=ItemPublic,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"description": "Referenced catalog, condition, or availability not found"}},
)
def create_item(item: ItemPost, session: Session = Depends(get_session)):
    _validate_item_refs(session, item.catalog_id, item.condition_id, item.availability_id)

    db_item = Item(**item.model_dump())
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.patch(
    "/{item_id}",
    response_model=ItemPublic,
    responses={404: {"description": "Item or referenced entity not found"}},
)
def update_item(
    item_id: int,
    item_patch: ItemPatch,
    session: Session = Depends(get_session),
):
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

    update_data = item_patch.model_dump(exclude_unset=True)
    _validate_item_refs(
        session,
        update_data.get("catalog_id"),
        update_data.get("condition_id"),
        update_data.get("availability_id"),
    )

    db_item.sqlmodel_update(update_data)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.post(
    "/{item_id}/soft-delete",
    response_model=ItemPublic,
    responses={404: {"description": "Item not found"}},
)
def soft_delete_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

    item.deleted = True
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.post(
    "/{item_id}/restore",
    response_model=ItemPublic,
    responses={404: {"description": "Item not found"}},
)
def restore_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

    item.deleted = False
    session.add(item)
    session.commit()
    session.refresh(item)
    return item
