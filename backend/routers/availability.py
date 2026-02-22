from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from db.database import get_session
from models.models import Availability
from schemas.availability import AvailabilityPatch, AvailabilityPost, AvailabilityPublic

router = APIRouter(
    prefix="/availabilities",
    tags=["availability"],
)


@router.get("/", response_model=list[AvailabilityPublic])
def get_availability(session: Session = Depends(get_session)):
    return session.exec(select(Availability)).all()


@router.get(
    "/{availability_id}",
    response_model=AvailabilityPublic,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Availability not found"},
    },
)
def get_availability_by_id(
    availability_id: int,
    session: Session = Depends(get_session),
):
    availability = session.get(Availability, availability_id)

    if not availability:
        raise HTTPException(status_code=404, detail=f"Availability with ID {availability_id} not found")

    return availability


@router.post("/", response_model=AvailabilityPublic, status_code=status.HTTP_201_CREATED)
def create_availability(
    availability: AvailabilityPost,
    session: Session = Depends(get_session),
):
    db_availability = Availability(**availability.model_dump())

    session.add(db_availability)
    session.commit()
    session.refresh(db_availability)

    return db_availability


@router.patch(
    "/{availability_id}",
    response_model=AvailabilityPublic,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Availability not found"},
    },
)
def update_availability(
    availability_id: int,
    availability_patch: AvailabilityPatch,
    session: Session = Depends(get_session),
):
    db_availability = session.get(Availability, availability_id)

    if not db_availability:
        raise HTTPException(
            status_code=404,
            detail=f"Availability {availability_id} not found",
        )

    update_data = availability_patch.model_dump(exclude_unset=True)

    db_availability.sqlmodel_update(update_data)

    session.add(db_availability)
    session.commit()
    session.refresh(db_availability)

    return db_availability


@router.delete(
    "/{availability_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "Availability not found"},
        409: {"description": "Availability still used by items"},
    },
)
def delete_availability(
    availability_id: int,
    session: Session = Depends(get_session),
):
    db_availability = session.get(Availability, availability_id)

    if not db_availability:
        raise HTTPException(
            status_code=404,
            detail=f"Availability {availability_id} not found",
        )

    try:
        session.delete(db_availability)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete availability: still used by items",
        ) from e
