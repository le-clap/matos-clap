from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import select, Session
from typing import List

from db.database import get_session
from models.models import Request, User

router = APIRouter(
    prefix="/request",
    tags=["request"],
)

@router.get("/", response_model=List[Request])
def get_requests(session: Session = Depends(get_session)):
    return session.exec(select(Request)).all()

@router.post("/", response_model=Request, status_code=status.HTTP_201_CREATED)
def create_request(
        request: Request,
        session: Session = Depends(get_session),
):
    if not session.get(User, request.borrower_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User {request.borrower_id} does not exist"
        )

    session.add(request)
    session.commit()

    session.refresh(request)

    return request
