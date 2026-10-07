from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles
from app.database import get_db
from app.models.user import User
from app.schemas.return_request import (
    ReturnCreate,
    ReturnReject,
    ReturnResponse,
)
from app.services.return_service import (
    approve_return,
    create_return_request,
    get_customer_returns,
    reject_return,
)

router = APIRouter(
    prefix="/returns",
    tags=["Returns"],
)


@router.post(
    "/orders/{order_id}",
    response_model=ReturnResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_return(
    order_id: int,
    data: ReturnCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        from app.models.order import Order

        order = db.get(Order, order_id)

        if not order:
            raise ValueError("Order not found")

        return create_return_request(
            db,
            order,
            current_user.id,
            data.reason,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[ReturnResponse],
)
def get_returns(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_customer_returns(
        db,
        current_user.id,
    )


@router.put(
    "/{return_id}/approve",
    response_model=ReturnResponse,
)
def approve_customer_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin")
    ),
):
    try:
        return approve_return(
            db,
            return_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.put(
    "/{return_id}/reject",
    response_model=ReturnResponse,
)
def reject_customer_return(
    return_id: int,
    data: ReturnReject,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin")
    ),
):
    try:
        return reject_return(
            db,
            return_id,
            data.reason,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )