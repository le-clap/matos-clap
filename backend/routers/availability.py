from fastapi import APIRouter, Depends, HTTPException, Path
from sqlmodel import select, Session
from typing import List

from db.database import get_session
from models.models import Availability

router = APIRouter(
    prefix="/availability",
    tags=["availability"],
)

@router.get("/", response_model=List[Availability])
# Depends lets FastAPI handle the closing of the session instead of relying on the context manager
def get_availability(session: Session = Depends(get_session)):
    return session.exec(select(Availability)).all()

@router.get("/search", response_model=Availability)
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

@router.get("/{availability_id}", response_model=Availability)
def get_availability_by_id(
        availability_id: int = Path(..., title="The ID of the availability status to get", gt=0),
        session: Session = Depends(get_session)
):
    # 1. Look for the record in the db
    availability = session.get(Availability, availability_id)

    # 2. Handle the case where the ID doesn't exist
    if not availability:
        raise HTTPException(
            status_code=404,
            detail=f"Availability with ID {availability_id} not found"
        )

    return availability