from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.user import User
from app.schemas.order import (
    OrderCreate,
    OrderStatus,
    OrderStatusUpdate,
)


def create_order(
    db: Session,
    order_data: OrderCreate,
    current_user: User | None = None,
) -> Order:
    if not order_data.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one item",
        )

    product_ids = [
        item.product_id
        for item in order_data.items
    ]

    if len(product_ids) != len(set(product_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate products are not allowed in the same order",
        )

    products = (
        db.query(Product)
        .filter(Product.id.in_(product_ids))
        .all()
    )

    product_map = {
        product.id: product
        for product in products
    }

    total_amount = Decimal("0.00")
    order_items = []

    for item_data in order_data.items:
        product = product_map.get(
            item_data.product_id
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Product {item_data.product_id} "
                    "not found"
                ),
            )

        if product.stock_quantity < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Insufficient stock for "
                    f"product '{product.name}'. "
                    f"Available stock: "
                    f"{product.stock_quantity}"
                ),
            )

        unit_price = Decimal(
            str(product.price)
        )

        subtotal = (
            unit_price * item_data.quantity
        )

        total_amount += subtotal

        order_item = OrderItem(
            product_id=product.id,
            quantity=item_data.quantity,
            unit_price=unit_price,
            subtotal=subtotal,
        )

        order_items.append(order_item)

    order = Order(
        customer_name=order_data.customer_name,
        customer_email=order_data.customer_email,
        user_id=(
            current_user.id
            if current_user
            else None
        ),
        total_amount=total_amount,
        status=OrderStatus.pending.value,
    )

    db.add(order)
    db.flush()

    for item_data, order_item in zip(
        order_data.items,
        order_items,
    ):
        product = product_map[
            item_data.product_id
        ]

        product.stock_quantity -= (
            item_data.quantity
        )

        order_item.order_id = order.id

        db.add(order_item)

    db.commit()
    db.refresh(order)

    return get_order(
        db,
        order.id,
    )


def get_order(
    db: Session,
    order_id: int,
) -> Order:
    order = (
        db.query(Order)
        .options(
            joinedload(Order.order_items)
        )
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return order


def get_orders(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    order_status: str | None = None,
    customer_email: str | None = None,
    current_user: User | None = None,
) -> list[Order]:
    query = (
        db.query(Order)
        .options(
            joinedload(Order.order_items)
        )
    )

    if current_user and current_user.role != "admin":
        query = query.filter(
            Order.user_id == current_user.id
        )

    if order_status:
        query = query.filter(
            Order.status == order_status
        )

    if customer_email:
        query = query.filter(
            Order.customer_email == customer_email
        )

    return (
        query
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_order_status(
    db: Session,
    order_id: int,
    status_data: OrderStatusUpdate,
) -> Order:
    order = get_order(
        db,
        order_id,
    )

    current_status = order.status
    new_status = status_data.status.value

    if current_status == OrderStatus.cancelled.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cancelled orders cannot be updated",
        )

    if current_status == OrderStatus.delivered.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Delivered orders cannot be updated",
        )

    if (
        new_status
        == OrderStatus.cancelled.value
        and current_status
        in {
            OrderStatus.shipped.value,
            OrderStatus.delivered.value,
        }
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Shipped or delivered orders cannot be cancelled",
        )

    order.status = new_status

    db.commit()
    db.refresh(order)

    return get_order(
        db,
        order.id,
    )