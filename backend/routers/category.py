from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from db.database import get_session
from models.models import Category

router = APIRouter(
    prefix="/categories",
    tags=["category"],
)


@router.get("/", response_model=list[Category])
def get_category(session: Session = Depends(get_session)):
    return session.exec(select(Category)).all()


@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(
    category: Category,
    session: Session = Depends(get_session),
):
    session.add(category)
    session.commit()

    session.refresh(category)

    return category
