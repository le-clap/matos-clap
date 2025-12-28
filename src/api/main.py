from fastapi import FastAPI, Depends, HTTPException, Path, status
from sqlmodel import select, Session
from contextlib import asynccontextmanager
from typing import List

from src.api.database import create_db_and_tables, get_session
from src.api.models import Availability, Items, Catalog, Categories, Condition
from src.api.seed import seed_data

# Create and initialize tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database...")
    create_db_and_tables()
    seed_data()

    yield

    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"status": "System Online"}

@app.get("/availability", response_model=List[Availability])
# Depends lets FastAPI handle the closing of the session instead of relying on the context manager
def get_availability(session: Session = Depends(get_session)):
    return session.exec(select(Availability)).all()

@app.get("/availability/search", response_model=Availability)
def get_availability_search(
        name: str = "Available",
        session: Session = Depends(get_session)):

    availability = session.exec(select(Availability).where(Availability.name == name)).first()

    if not availability:
        raise HTTPException(
            status_code=404,
            detail=f"Availability class {name} not found"
        )

    return availability

@app.get("/availability/{availability_id}", response_model=Availability)
def get_availability_by_id(
        availability_id: int = Path(..., title="The ID of the availability status to get", gt=0),
        session: Session = Depends(get_session)
):
    # 1. Look for the record in the database
    availability = session.get(Availability, availability_id)

    # 2. Handle the case where the ID doesn't exist
    if not availability:
        raise HTTPException(
            status_code=404,
            detail=f"Availability with ID {availability_id} not found"
        )

    return availability

@app.get("/categories", response_model=List[Categories])
def get_categories(session: Session = Depends(get_session)):
    return session.exec(select(Categories)).all()

@app.get("/catalog", response_model=List[Catalog])
def get_catalogs(session: Session = Depends(get_session)):
    catalog = session.exec(select(Catalog)).all()
    return catalog

@app.get("/item", response_model=List[Items])
def get_items(session: Session = Depends(get_session)):
    item = session.exec(select(Items)).all()
    return item

@app.post("/categories", response_model=Categories, status_code=status.HTTP_201_CREATED)
def create_category(
        category: Categories,
        session: Session = Depends(get_session),
):

    session.add(category)
    session.commit()

    session.refresh(category)

    return category

@app.post("/catalog", response_model=Catalog, status_code=status.HTTP_201_CREATED)
def create_catalog_entry(
        catalog_entry: Catalog,
        session: Session = Depends(get_session),
):
    if not session.get(Categories, catalog_entry.category_id):
        raise HTTPException(
            status_code=404,
            detail=f"Category {catalog_entry.category_id} not found"
        )

    session.add(catalog_entry)
    session.commit()

    session.refresh(catalog_entry)

    return catalog_entry


@app.post("/items/", response_model=Items, status_code=status.HTTP_201_CREATED)
def create_item(item: Items, session: Session = Depends(get_session)):
    # 1. Validation check (Optional but recommended)
    # You could check here if the catalog_id actually exists before saving
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

    # 3. Commit to save it to database.db
    session.commit()

    # 4. Refresh to get the auto-generated ID back from the DB
    session.refresh(item)

    return item


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, session: Session = Depends(get_session)):
    # 1. Fetch the object
    item = session.get(Items, item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # 2. Delete it
    session.delete(item)

    # 3. Commit
    session.commit()

    # 4. Return nothing (Standard for 204 No Content)
    return None

@app.patch("/items/{item_id}/soft-delete", response_model=Items)
def soft_delete_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Items, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.deleted = True
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@app.patch("/items/{item_id}/soft-undelete", response_model=Items)
def soft_undelete_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Items, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.deleted = False
    session.add(item)
    session.commit()
    session.refresh(item)
    return item