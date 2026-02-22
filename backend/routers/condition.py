from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from db.database import get_session
from models.models import Condition
from schemas.condition import ConditionPatch, ConditionPost, ConditionPublic

router = APIRouter(
    prefix="/conditions",
    tags=["condition"],
)


@router.get("/", response_model=list[ConditionPublic])
def get_conditions(session: Session = Depends(get_session)):
    return session.exec(select(Condition)).all()


@router.get(
    "/{condition_id}",
    response_model=ConditionPublic,
    responses={404: {"description": "Condition not found"}},
)
def get_condition_by_id(condition_id: int, session: Session = Depends(get_session)):
    condition = session.get(Condition, condition_id)
    if not condition:
        raise HTTPException(status_code=404, detail=f"Condition with ID {condition_id} not found")
    return condition


@router.post("/", response_model=ConditionPublic, status_code=status.HTTP_201_CREATED)
def create_condition(condition: ConditionPost, session: Session = Depends(get_session)):
    db_condition = Condition(**condition.model_dump())
    session.add(db_condition)
    session.commit()
    session.refresh(db_condition)
    return db_condition


@router.patch(
    "/{condition_id}",
    response_model=ConditionPublic,
    responses={404: {"description": "Condition not found"}},
)
def update_condition(
    condition_id: int,
    condition_patch: ConditionPatch,
    session: Session = Depends(get_session),
):
    db_condition = session.get(Condition, condition_id)
    if not db_condition:
        raise HTTPException(status_code=404, detail=f"Condition with ID {condition_id} not found")

    db_condition.sqlmodel_update(condition_patch.model_dump(exclude_unset=True))
    session.add(db_condition)
    session.commit()
    session.refresh(db_condition)
    return db_condition


@router.delete(
    "/{condition_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "Condition not found"},
        409: {"description": "Condition still used by items"},
    },
)
def delete_condition(condition_id: int, session: Session = Depends(get_session)):
    db_condition = session.get(Condition, condition_id)
    if not db_condition:
        raise HTTPException(status_code=404, detail=f"Condition with ID {condition_id} not found")

    try:
        session.delete(db_condition)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete condition: still used by items",
        ) from e
