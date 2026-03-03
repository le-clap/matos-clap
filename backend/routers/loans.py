from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import Session, select

from db.database import get_session
from dependencies.auth import get_current_user, has_role, require_role
from models.enums import AccessLevel
from models.models import Item, Loan, LoanedItem, Request, User
from schemas.loans import LoanedItemPatch, LoanedItemPublic, LoanPatch, LoanPost, LoanPublic

router = APIRouter(
    prefix="/loans",
    tags=["loans"],
)


def _loan_load_options():
    return [
        joinedload(Loan.borrower),  # ty: ignore[invalid-argument-type]
        joinedload(Loan.assignee),  # ty: ignore[invalid-argument-type]
        selectinload(Loan.loaned_items).joinedload(LoanedItem.item),  # ty: ignore[invalid-argument-type]
    ]


@router.get("/", response_model=list[LoanPublic])
def get_loans(
    borrower_id: int | None = None,
    active: bool | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not has_role(current_user, AccessLevel.CLAP):
        borrower_id = current_user.id
    if borrower_id is not None and not session.get(User, borrower_id):
        raise HTTPException(status_code=404, detail=f"User with ID {borrower_id} not found")
    statement = select(Loan).options(*_loan_load_options())
    if borrower_id is not None:
        statement = statement.where(Loan.borrower_id == borrower_id)
    if active is True:
        statement = statement.where(Loan.actual_return_date.is_(None))  # type: ignore[union-attr]
    elif active is False:
        statement = statement.where(Loan.actual_return_date.is_not(None))  # type: ignore[union-attr]
    return session.exec(statement).unique().all()


@router.get(
    "/{loan_id}",
    response_model=LoanPublic,
    responses={404: {"description": "Loan not found"}},
)
def get_loan_by_id(
    loan_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)
):
    statement = select(Loan).where(Loan.id == loan_id).options(*_loan_load_options())
    loan = session.exec(statement).unique().first()
    if not loan:
        raise HTTPException(status_code=404, detail=f"Loan with ID {loan_id} not found")
    if not has_role(current_user, AccessLevel.CLAP) and loan.borrower_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return loan


@router.post(
    "/",
    response_model=LoanPublic,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"description": "Referenced user, request, or item not found"}},
)
def create_loan(
    loan_data: LoanPost, session: Session = Depends(get_session), _user=Depends(require_role(AccessLevel.CLAP))
):
    if not session.get(User, loan_data.borrower_id):
        raise HTTPException(status_code=404, detail=f"Borrower with ID {loan_data.borrower_id} not found")
    if not session.get(User, loan_data.assignee_id):
        raise HTTPException(status_code=404, detail=f"Assignee with ID {loan_data.assignee_id} not found")
    if loan_data.request_id is not None and not session.get(Request, loan_data.request_id):
        raise HTTPException(status_code=404, detail=f"Request with ID {loan_data.request_id} not found")

    for li in loan_data.loaned_items:
        if not session.get(Item, li.item_id):
            raise HTTPException(status_code=404, detail=f"Item with ID {li.item_id} not found")

    db_loan = Loan(
        borrower_id=loan_data.borrower_id,
        assignee_id=loan_data.assignee_id,
        start_date=loan_data.start_date,
        end_date=loan_data.end_date,
        total_deposit_cents=loan_data.total_deposit_cents,
        request_id=loan_data.request_id,
        comments=loan_data.comments,
    )
    session.add(db_loan)
    session.flush()

    assert db_loan.id is not None

    for li in loan_data.loaned_items:
        db_li = LoanedItem(
            loan_id=db_loan.id,
            item_id=li.item_id,
        )
        session.add(db_li)

    session.commit()
    session.refresh(db_loan)
    return db_loan


@router.patch(
    "/{loan_id}",
    response_model=LoanPublic,
    responses={404: {"description": "Loan not found"}},
)
def update_loan(
    loan_id: int,
    loan_patch: LoanPatch,
    session: Session = Depends(get_session),
    _user=Depends(require_role(AccessLevel.CLAP)),
):
    db_loan = session.get(Loan, loan_id)
    if not db_loan:
        raise HTTPException(status_code=404, detail=f"Loan with ID {loan_id} not found")

    db_loan.sqlmodel_update(loan_patch.model_dump(exclude_unset=True))
    session.add(db_loan)
    session.commit()
    session.refresh(db_loan)
    return db_loan


@router.delete(
    "/{loan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Loan not found"}},
)
def delete_loan(loan_id: int, session: Session = Depends(get_session), _user=Depends(require_role(AccessLevel.CLAP))):
    db_loan = session.get(Loan, loan_id)
    if not db_loan:
        raise HTTPException(status_code=404, detail=f"Loan with ID {loan_id} not found")

    session.delete(db_loan)
    session.commit()


@router.patch(
    "/{loan_id}/items/{loaned_item_id}",
    response_model=LoanedItemPublic,
    responses={404: {"description": "Loan or loaned item not found"}},
)
def update_loaned_item(
    loan_id: int,
    loaned_item_id: int,
    loaned_item_patch: LoanedItemPatch,
    session: Session = Depends(get_session),
    _user=Depends(require_role(AccessLevel.CLAP)),
):
    statement = (
        select(LoanedItem)
        .where(LoanedItem.id == loaned_item_id, LoanedItem.loan_id == loan_id)
        .options(
            joinedload(LoanedItem.item),  # ty: ignore[invalid-argument-type]
        )
    )
    db_li = session.exec(statement).first()
    if not db_li:
        raise HTTPException(status_code=404, detail=f"Loaned item {loaned_item_id} not found in loan {loan_id}")

    db_li.sqlmodel_update(loaned_item_patch.model_dump(exclude_unset=True))
    session.add(db_li)
    session.commit()
    session.refresh(db_li)
    return db_li
