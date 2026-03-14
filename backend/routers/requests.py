from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import Session, asc, select

from db.database import get_session
from dependencies.auth import get_current_user, has_role, require_role
from models.enums import AccessLevel
from models.models import Catalog, Request, RequestedCatalog, User
from schemas.requests import RequestPatch, RequestPost, RequestPublic

router = APIRouter(
    prefix="/requests",
    tags=["requests"],
)


def _request_load_options():
    return [
        joinedload(Request.borrower),  # ty: ignore[invalid-argument-type]
        selectinload(Request.requested_catalogs).joinedload(  # ty: ignore[invalid-argument-type]
            RequestedCatalog.catalog  # ty: ignore[invalid-argument-type]
        ),
    ]


@router.get("/", response_model=list[RequestPublic])
def get_requests(
    borrower_id: int | None = None,
    processed: bool | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not has_role(current_user, AccessLevel.CLAP):
        borrower_id = current_user.id
    if borrower_id is not None and not session.get(User, borrower_id):
        raise HTTPException(status_code=404, detail=f"User with ID {borrower_id} not found")
    statement = select(Request).options(*_request_load_options()).order_by(asc(Request.start_date))
    if borrower_id is not None:
        statement = statement.where(Request.borrower_id == borrower_id)
    if processed is not None:
        statement = statement.where(Request.processed == processed)

    return session.exec(statement).unique().all()


@router.get(
    "/{request_id}",
    response_model=RequestPublic,
    responses={404: {"description": "Request not found"}},
)
def get_request_by_id(
    request_id: int, session: Session = Depends(get_session), _user=Depends(require_role(AccessLevel.CLAP))
):
    statement = select(Request).where(Request.id == request_id).options(*_request_load_options())
    db_request = session.exec(statement).unique().first()
    if not db_request:
        raise HTTPException(status_code=404, detail=f"Request with ID {request_id} not found")
    return db_request


@router.post(
    "/",
    response_model=RequestPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        403: {"description": "Attempt to create request for another user"},
        404: {"description": "Borrower or catalog not found"},
    },
)
def create_request(
    request_data: RequestPost, session: Session = Depends(get_session), user=Depends(require_role(AccessLevel.USER))
):
    if user.id != request_data.borrower_id:
        raise HTTPException(status_code=403, detail="You can not create requests for other users")
    if not session.get(User, request_data.borrower_id):
        raise HTTPException(status_code=404, detail=f"User with ID {request_data.borrower_id} not found")

    for rc in request_data.requested_catalogs:
        if not session.get(Catalog, rc.catalog_id):
            raise HTTPException(status_code=404, detail=f"Catalog with ID {rc.catalog_id} not found")

    db_request = Request(
        borrower_id=request_data.borrower_id,
        phone_number=request_data.phone_number,
        start_date=request_data.start_date,
        end_date=request_data.end_date,
        reason=request_data.reason,
    )
    session.add(db_request)
    session.flush()

    assert db_request.id is not None

    for rc in request_data.requested_catalogs:
        db_rc = RequestedCatalog(
            request_id=db_request.id,
            catalog_id=rc.catalog_id,
            quantity=rc.quantity,
        )
        session.add(db_rc)

    session.commit()
    session.refresh(db_request)
    return db_request


@router.patch(
    "/{request_id}",
    response_model=RequestPublic,
    responses={404: {"description": "Request not found"}},
)
def update_request(
    request_id: int,
    request_patch: RequestPatch,
    session: Session = Depends(get_session),
    _user=Depends(require_role(AccessLevel.CLAP)),
):
    db_request = session.get(Request, request_id)
    if not db_request:
        raise HTTPException(status_code=404, detail=f"Request with ID {request_id} not found")

    db_request.sqlmodel_update(request_patch.model_dump(exclude_unset=True))
    session.add(db_request)
    session.commit()
    session.refresh(db_request)
    return db_request


@router.delete(
    "/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Request not found"}},
)
def delete_request(
    request_id: int, session: Session = Depends(get_session), _user=Depends(require_role(AccessLevel.CLAP))
):
    db_request = session.get(Request, request_id)
    if not db_request:
        raise HTTPException(status_code=404, detail=f"Request with ID {request_id} not found")

    session.delete(db_request)
    session.commit()
