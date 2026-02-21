from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from db.database import get_session
from models.models import Loan, Request, User

router = APIRouter(
    prefix="/loans",
    tags=["loan"],
)


@router.get("/", response_model=list[Loan])
def get_loans(session: Session = Depends(get_session)):
    return session.exec(select(Loan)).all()


@router.post("/", response_model=Loan, status_code=status.HTTP_201_CREATED)
def create_loan(
    loan: Loan,
    session: Session = Depends(get_session),
):
    if not session.get(Request, loan.request_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Request ID {loan.request_id} does not exist"
        )

    if not session.get(User, loan.borrower_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Borrower {loan.borrower_id} does not exist")

    if not session.get(User, loan.assignee_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Assignee {loan.assignee_id} does not exist")

    session.add(loan)
    session.commit()

    session.refresh(loan)

    return loan
