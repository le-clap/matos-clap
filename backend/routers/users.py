from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import Session, select

from db.database import get_session
from models.models import Loan, LoanedItem, Request, RequestedCatalog, User
from schemas.loans import LoanPublic
from schemas.requests import RequestPublic
from schemas.users import UserPatch, UserPost, UserPublic

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/", response_model=list[UserPublic])
def get_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()


@router.get(
    "/{user_id}",
    response_model=UserPublic,
    responses={404: {"description": "User not found"}},
)
def get_user_by_id(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
    return user


@router.post(
    "/",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "Username or email already exists"}},
)
def create_user(user: UserPost, session: Session = Depends(get_session)):
    db_user = User(**user.model_dump())

    try:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="A user with this username or email already exists",
        ) from e

    return db_user


@router.patch(
    "/{user_id}",
    response_model=UserPublic,
    responses={
        404: {"description": "User not found"},
        409: {"description": "Username or email already exists"},
    },
)
def update_user(
    user_id: int,
    user_patch: UserPatch,
    session: Session = Depends(get_session),
):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

    db_user.sqlmodel_update(user_patch.model_dump(exclude_unset=True))

    try:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="A user with this username or email already exists",
        ) from e

    return db_user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "User not found"},
        409: {"description": "User still referenced by requests or loans"},
    },
)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

    try:
        session.delete(db_user)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete user: still referenced by requests or loans",
        ) from e


@router.get(
    "/{user_id}/requests",
    response_model=list[RequestPublic],
    responses={404: {"description": "User not found"}},
)
def get_user_requests(user_id: int, processed: bool | None = None, session: Session = Depends(get_session)):
    if not session.get(User, user_id):
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

    statement = (
        select(Request)
        .where(Request.borrower_id == user_id)
        .options(
            joinedload(Request.borrower),  # ty: ignore[invalid-argument-type]
            selectinload(Request.requested_catalogs).joinedload(  # ty: ignore[invalid-argument-type]
                RequestedCatalog.catalog  # ty: ignore[invalid-argument-type]
            ),
        )
    )
    if processed is not None:
        statement = statement.where(Request.processed == processed)
    return session.exec(statement).unique().all()


@router.get(
    "/{user_id}/loans",
    response_model=list[LoanPublic],
    responses={404: {"description": "User not found"}},
)
def get_user_loans(user_id: int, active: bool | None = None, session: Session = Depends(get_session)):
    if not session.get(User, user_id):
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

    statement = (
        select(Loan)
        .where(Loan.borrower_id == user_id)
        .options(
            joinedload(Loan.borrower),  # ty: ignore[invalid-argument-type]
            joinedload(Loan.assignee),  # ty: ignore[invalid-argument-type]
            selectinload(Loan.loaned_items).joinedload(LoanedItem.item),  # ty: ignore[invalid-argument-type]
        )
    )
    if active is True:
        statement = statement.where(Loan.actual_return_date.is_(None))  # type: ignore[union-attr]
    elif active is False:
        statement = statement.where(Loan.actual_return_date.is_not(None))  # type: ignore[union-attr]
    return session.exec(statement).unique().all()
