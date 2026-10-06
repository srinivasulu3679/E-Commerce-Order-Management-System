from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
)
from app.services.order_service import (
    create_order,
    get_order,
    get_orders,
    update_order_status,
)


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order_endpoint(
    order_data: OrderCreate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    return create_order(
        db=db,
        order_data=order_data,
        current_user=current_user,
    )


@router.get(
    "",
    response_model=list[OrderResponse],
)
def list_orders(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    order_status: str | None = Query(
        default=None,
        min_length=1,
        max_length=30,
    ),
    customer_email: str | None = Query(
        default=None,
        min_length=3,
        max_length=150,
    ),
):
    return get_orders(
        db=db,
        skip=skip,
        limit=limit,
        order_status=order_status,
        customer_email=customer_email,
        current_user=current_user,
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_order_endpoint(
    order_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    order = get_order(
        db,
        order_id,
    )

    if (
        current_user.role != "admin"
        and order.user_id != current_user.id
    ):
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own orders",
        )

    return order


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
)
def update_order_status_endpoint(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    _: Annotated[
        User,
        Depends(require_admin),
    ],
):
    return update_order_status(
        db=db,
        order_id=order_id,
        status_data=status_data,
    )