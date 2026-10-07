
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.order import OrderResponse, OrderStatusUpdate
from app.services.order import (
    cancel_order,
    create_order_from_cart,
    get_customer_order,
    get_customer_orders,
    update_order_status,
)


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


def build_order_response(order):
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        customer_id=order.customer_id,
        address_id=order.address_id,
        subtotal=order.subtotal,
        tax_amount=order.tax_amount,
        delivery_charge=order.delivery_charge,
        grand_total=order.grand_total,
        status=order.status,
        payment_status=order.payment_status,
        delivered_at=order.delivered_at,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=order.order_items,
    )


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order_endpoint(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    address_id: int = Query(..., gt=0),
):
    try:
        order = create_order_from_cart(
            db,
            current_user.id,
            address_id,
        )
        return build_order_response(order)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[OrderResponse],
)
def list_orders(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    if current_user.role == "admin":
        from app.models.order import Order

        orders = (
            db.query(Order)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    else:
        orders = get_customer_orders(
            db,
            current_user.id,
            skip,
            limit,
        )

    return [build_order_response(order) for order in orders]


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_order_endpoint(
    order_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        order = get_customer_order(
            db,
            order_id,
            current_user.id,
            current_user.role,
        )
        return build_order_response(order)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
)
def cancel_order_endpoint(
    order_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        order = cancel_order(
            db,
            order_id,
            current_user.id,
        )
        return build_order_response(order)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
)
def update_order_status_endpoint(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    from app.models.order import Order

    order = db.get(Order, order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    try:
        order = update_order_status(
            db,
            order,
            status_data.status,
        )

        return build_order_response(order)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
