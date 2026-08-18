"""Request management endpoints."""

from datetime import UTC, datetime
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import func
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import Session, asc, col, select

from db.database import get_session
from dependencies.auth import get_current_user, has_role, require_role
from models.enums import AccessLevel, Availability, RequestStatus
from models.models import Catalog, Item, Request, RequestedCatalog, User
from schemas.catalogs import CatalogBrief
from schemas.requests import (
    RequestedCatalogRecommendation,
    RequestPatch,
    RequestPost,
    RequestPublic,
    RequestRecommendationItem,
    RequestRecommendationsResponse,
)
from schemas.utils import PaginatedResponse, PaginationParams
from services.inventory import find_busy_item_ids

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/requests", tags=["requests"])

# Dependency type aliases
SessionDep = Annotated[Session, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
ClapDep = Annotated[User, Depends(require_role(AccessLevel.CLAP))]


def _ensure_aware(dt: datetime) -> datetime:
    """Normalize a potentially naive datetime to UTC."""
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


def _request_load_options():
    return [
        joinedload(Request.borrower),  # ty: ignore[invalid-argument-type]
        selectinload(Request.loan),  # ty: ignore[invalid-argument-type]
        selectinload(Request.requested_catalogs).joinedload(  # ty: ignore[invalid-argument-type]
            RequestedCatalog.catalog  # ty: ignore[invalid-argument-type]
        ),
    ]


@router.get("/", response_model=PaginatedResponse[RequestPublic])
def get_requests(
    session: SessionDep,
    current_user: CurrentUserDep,
    pagination: Annotated[PaginationParams, Depends()],
    borrower_id: Annotated[int | None, Query()] = None,
    processed: Annotated[bool | None, Query()] = None,
) -> PaginatedResponse[Request]:
    effective_borrower_id = borrower_id
    if not has_role(current_user, AccessLevel.CLAP):
        effective_borrower_id = current_user.id
    if effective_borrower_id is not None and not session.get(User, effective_borrower_id):
        raise HTTPException(status_code=404, detail=f"User with ID {effective_borrower_id} not found")

    base_statement = select(Request)
    if effective_borrower_id is not None:
        base_statement = base_statement.where(Request.borrower_id == effective_borrower_id)
    elif pagination.search is not None:
        base_statement = base_statement.join(Request.borrower).where(  # ty: ignore[invalid-argument-type]
            col(User.name).ilike(f"%{pagination.search}%")
        )
    if processed is not None:
        processed_statuses = {
            True: [RequestStatus.APPROVED, RequestStatus.REFUSED],
            False: [RequestStatus.PENDING],
        }
        base_statement = base_statement.where(col(Request.status).in_(processed_statuses[processed]))

    total = session.exec(select(func.count()).select_from(base_statement.subquery())).one()

    statement = (
        base_statement.options(*_request_load_options())
        .order_by(asc(Request.start_date), asc(Request.id))
        .offset(pagination.offset())
        .limit(pagination.limit)
    )
    requests = session.exec(statement).all()

    return PaginatedResponse(
        items=list(requests),
        total=total,
        limit=pagination.limit,
        page=pagination.page,
        search=pagination.search,
    )


@router.get(
    "/{request_id}/recommendations",
    response_model=RequestRecommendationsResponse,
    responses={404: {"description": "Request not found"}},
)
def get_request_recommendations(
    session: SessionDep,
    _user: ClapDep,
    request_id: Annotated[int, Path(ge=1)],
) -> RequestRecommendationsResponse:
    statement = select(Request).where(Request.id == request_id).options(*_request_load_options())
    db_request = session.exec(statement).first()
    if not db_request:
        raise HTTPException(status_code=404, detail=f"Request with ID {request_id} not found")

    recommendations: list[RequestedCatalogRecommendation] = []
    if db_request.id is None:
        raise HTTPException(status_code=500, detail="Invalid request ID")

    for requested_catalog in db_request.requested_catalogs:
        if requested_catalog.id is None:
            raise HTTPException(status_code=500, detail="Invalid requested catalog ID")
        items = session.exec(
            select(Item)
            .where(
                Item.catalog_id == requested_catalog.catalog_id,
                col(Item.deleted_at).is_(None),
            )
            .order_by(asc(Item.id))
        ).all()

        item_ids = [item.id for item in items if item.id is not None]
        busy_item_ids = find_busy_item_ids(session, item_ids, db_request.start_date, db_request.end_date)

        candidate_items: list[RequestRecommendationItem] = []
        recommended_item_ids: list[int] = []
        for item in items:
            has_date_conflict = item.id in busy_item_ids
            warning: str | None = None
            if item.availability != Availability.AVAILABLE and has_date_conflict:
                warning = "Item is not marked available and conflicts with another active loan"
            elif item.availability != Availability.AVAILABLE:
                warning = "Item is not marked available"
            elif has_date_conflict:
                warning = "Item conflicts with another active loan for the requested dates"
            else:
                if item.id is not None and len(recommended_item_ids) < requested_catalog.quantity:
                    recommended_item_ids.append(item.id)

            if item.id is None:
                continue

            candidate_items.append(
                RequestRecommendationItem(
                    item_id=item.id,
                    item_name=item.name,
                    availability=item.availability,
                    has_date_conflict=has_date_conflict,
                    warning=warning,
                )
            )

        warnings: list[str] = []
        if len(recommended_item_ids) < requested_catalog.quantity:
            warnings.append(
                f"Only {len(recommended_item_ids)} recommended item(s) found for requested quantity "
                f"{requested_catalog.quantity}"
            )

        if requested_catalog.catalog.id is None:
            raise HTTPException(status_code=500, detail="Invalid catalog reference found in request")

        recommendations.append(
            RequestedCatalogRecommendation(
                requested_catalog_id=requested_catalog.id,
                catalog=CatalogBrief(
                    id=requested_catalog.catalog.id,
                    name=requested_catalog.catalog.name,
                    image_path=requested_catalog.catalog.image_path,
                ),
                requested_quantity=requested_catalog.quantity,
                recommended_item_ids=recommended_item_ids,
                candidate_items=candidate_items,
                warnings=warnings,
            )
        )

    return RequestRecommendationsResponse(
        request_id=db_request.id,
        start_date=db_request.start_date,
        end_date=db_request.end_date,
        recommendations=recommendations,
    )


@router.get(
    "/{request_id}",
    response_model=RequestPublic,
    responses={404: {"description": "Request not found"}},
)
def get_request_by_id(
    session: SessionDep,
    _user: ClapDep,
    request_id: Annotated[int, Path(ge=1)],
) -> Request:
    statement = select(Request).where(Request.id == request_id).options(*_request_load_options())
    db_request = session.exec(statement).first()
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
    session: SessionDep,
    current_user: CurrentUserDep,
    request_data: RequestPost,
) -> Request:
    if current_user.id != request_data.borrower_id:
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

    if db_request.id is None:
        raise HTTPException(status_code=500, detail="Failed to create request")

    for rc in request_data.requested_catalogs:
        db_rc = RequestedCatalog(
            request_id=db_request.id,
            catalog_id=rc.catalog_id,
            quantity=rc.quantity,
        )
        session.add(db_rc)

    session.commit()
    session.refresh(db_request)

    logger.info("request.created", request_id=db_request.id)
    return db_request


@router.patch(
    "/{request_id}",
    response_model=RequestPublic,
    responses={
        403: {"description": "Not allowed to edit this request"},
        404: {"description": "Request not found"},
        409: {"description": "Request can no longer be edited"},
    },
)
def update_request(
    session: SessionDep,
    current_user: CurrentUserDep,
    request_id: Annotated[int, Path(ge=1)],
    request_patch: RequestPatch,
) -> Request:
    statement = select(Request).where(Request.id == request_id).options(*_request_load_options())
    db_request = session.exec(statement).first()
    if not db_request:
        raise HTTPException(status_code=404, detail=f"Request with ID {request_id} not found")

    # A borrower may edit their own request only while it is still pending.
    if not has_role(current_user, AccessLevel.CLAP):
        if db_request.borrower_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only edit your own requests")
        if db_request.processed:
            raise HTTPException(status_code=409, detail="A processed request can no longer be edited")
        if request_patch.status is not None:
            raise HTTPException(status_code=403, detail="You cannot change the status")

    # The resulting period must stay valid even when only one bound is patched.
    new_start = request_patch.start_date or db_request.start_date
    new_end = request_patch.end_date or db_request.end_date
    if _ensure_aware(new_start) >= _ensure_aware(new_end):
        raise HTTPException(status_code=422, detail="start_date must be before end_date")

    db_request.sqlmodel_update(request_patch.model_dump(exclude_unset=True))
    session.add(db_request)
    session.commit()
    session.refresh(db_request)
    return db_request


@router.delete(
    "/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        403: {"description": "Not allowed to delete this request"},
        404: {"description": "Request not found"},
        409: {"description": "Request can no longer be deleted"},
    },
)
def delete_request(
    session: SessionDep,
    current_user: CurrentUserDep,
    request_id: Annotated[int, Path(ge=1)],
) -> None:
    db_request = session.get(Request, request_id)
    if not db_request:
        raise HTTPException(status_code=404, detail=f"Request with ID {request_id} not found")

    # A borrower may delete their own request only while it is still pending.
    if not has_role(current_user, AccessLevel.CLAP):
        if db_request.borrower_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only delete your own requests")
        if db_request.processed:
            raise HTTPException(status_code=409, detail="A processed request can no longer be deleted")

    session.delete(db_request)
    session.commit()

    logger.info("request.deleted", request_id=request_id)
