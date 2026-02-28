from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from db.database import get_session
from dependencies.auth import require_role
from models.enums import AccessLevel, Availability, Condition
from models.models import Catalog, Item
from schemas.items import ItemPatch, ItemPost, ItemPublic

router = APIRouter(
    prefix="/items",
    tags=["items"],
)


def _item_load_options():
    return [
        joinedload(Item.catalog).joinedload(Catalog.category),  # ty: ignore[invalid-argument-type]
    ]


@router.get("/", response_model=list[ItemPublic])
def get_items(
    availability: Availability | None = None,
    condition: Condition | None = None,
    session: Session = Depends(get_session),
):
    statement = select(Item).options(*_item_load_options()).where(Item.deleted_at == None)  # noqa: E711 noqa: E712
    if availability is not None:
        statement = statement.where(Item.availability == availability)
    if condition is not None:
        statement = statement.where(Item.condition == condition)
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
    responses={404: {"description": "Referenced catalog not found"}},
)
def create_item(
    item: ItemPost, session: Session = Depends(get_session), _user=Depends(require_role(AccessLevel.MANAGER))
):
    if not session.get(Catalog, item.catalog_id):
        raise HTTPException(status_code=404, detail=f"Catalog with ID {item.catalog_id} not found")

    db_item = Item(**item.model_dump())
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.patch(
    "/{item_id}",
    response_model=ItemPublic,
    responses={404: {"description": "Item or referenced catalog not found"}},
)
def update_item(
    item_id: int,
    item_patch: ItemPatch,
    session: Session = Depends(get_session),
    _user=Depends(require_role(AccessLevel.MANAGER)),
):
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

    update_data = item_patch.model_dump(exclude_unset=True)
    if "catalog_id" in update_data and not session.get(Catalog, update_data["catalog_id"]):
        raise HTTPException(status_code=404, detail=f"Catalog with ID {update_data['catalog_id']} not found")

    db_item.sqlmodel_update(update_data)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Item not found"}},
)
def soft_delete_item(
    item_id: int, session: Session = Depends(get_session), _user=Depends(require_role(AccessLevel.MANAGER))
):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

    item.deleted = True
    session.add(item)
    session.commit()
