from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.address import Address
from app.models.cart import Cart
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.product import Product


TAX_RATE = Decimal("0.18")
DELIVERY_CHARGE = Decimal("50.00")
FREE_DELIVERY_LIMIT = Decimal("500.00")


def generate_order_number() -> str:
    return f"ORD-{uuid.uuid4().hex[:12].upper()}"


def calculate_order_totals(subtotal: Decimal):
    tax_amount = (
        subtotal * TAX_RATE
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    delivery_charge = (
        Decimal("0.00")
        if subtotal > FREE_DELIVERY_LIMIT
        else DELIVERY_CHARGE
    )

    grand_total = subtotal + tax_amount + delivery_charge

    return (
        subtotal,
        tax_amount,
        delivery_charge,
        grand_total,
    )


def create_order_from_cart(
    db: Session,
    customer_id: int,
    address_id: int,
) -> Order:
    try:
        cart = db.scalar(
            select(Cart)
            .where(Cart.customer_id == customer_id)
            .with_for_update()
        )

        if not cart:
            raise ValueError("Cart not found")

        if not cart.items:
            raise ValueError("Cart is empty")

        address = db.scalar(
            select(Address).where(
                Address.id == address_id,
                Address.customer_id == customer_id,
            )
        )

        if not address:
            raise ValueError("Address not found")

        subtotal = Decimal("0.00")

        for cart_item in cart.items:
            product = db.scalar(
                select(Product)
                .where(Product.id == cart_item.product_id)
                .with_for_update()
            )

            if not product:
                raise ValueError(
                    f"Product {cart_item.product_id} not found"
                )

            if not product.is_active:
                raise ValueError(
                    f"Product '{product.name}' is inactive"
                )

            if cart_item.quantity < 1:
                raise ValueError(
                    f"Invalid quantity for product '{product.name}'"
                )

            if cart_item.quantity > product.stock_quantity:
                raise ValueError(
                    f"Insufficient stock for '{product.name}'. "
                    f"Available: {product.stock_quantity}"
                )

            subtotal += product.price * cart_item.quantity

        subtotal = subtotal.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        (
            subtotal,
            tax_amount,
            delivery_charge,
            grand_total,
        ) = calculate_order_totals(subtotal)

        order = Order(
            order_number=generate_order_number(),
            customer_id=customer_id,
            address_id=address_id,
            subtotal=subtotal,
            tax_amount=tax_amount,
            delivery_charge=delivery_charge,
            grand_total=grand_total,
            status="Pending",
            payment_status="Unpaid",
        )

        db.add(order)
        db.flush()

        for cart_item in cart.items:
            product = db.scalar(
                select(Product)
                .where(Product.id == cart_item.product_id)
                .with_for_update()
            )

            line_total = (
                product.price * cart_item.quantity
            ).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=cart_item.quantity,
                unit_price=product.price,
                line_total=line_total,
            )

            db.add(order_item)

            product.stock_quantity -= cart_item.quantity

        for cart_item in list(cart.items):
            db.delete(cart_item)

        db.commit()
        db.refresh(order)

        return order

    except Exception:
        db.rollback()
        raise


def get_customer_orders(
    db: Session,
    customer_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[Order]:
    return list(
        db.scalars(
            select(Order)
            .where(Order.customer_id == customer_id)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).all()
    )


def get_customer_order(
    db: Session,
    order_id: int,
    customer_id: int,
    role: str = "customer",
) -> Order:
    if role == "admin":
        order = db.get(Order, order_id)
    else:
        order = db.scalar(
            select(Order).where(
                Order.id == order_id,
                Order.customer_id == customer_id,
            )
        )

    if not order:
        raise ValueError("Order not found")

    return order


def cancel_order(
    db: Session,
    order: Order,
) -> Order:
    if order.status not in {"Pending", "Confirmed"}:
        raise ValueError(
            "Only Pending or Confirmed orders can be cancelled"
        )

    try:
        for item in order.order_items:
            product = db.scalar(
                select(Product)
                .where(Product.id == item.product_id)
                .with_for_update()
            )

            if product:
                product.stock_quantity += item.quantity

        order.status = "Cancelled"

        if order.payment_status == "Paid":
            order.payment_status = "Refunded"

            payments = db.scalars(
                select(Payment).where(
                    Payment.order_id == order.id,
                    Payment.status == "Success",
                )
            ).all()

            for payment in payments:
                payment.status = "Refunded"

        db.commit()
        db.refresh(order)

        return order

    except Exception:
        db.rollback()
        raise


def update_order_status(
    db: Session,
    order: Order,
    new_status: str,
) -> Order:
    allowed_statuses = {
        "Pending": 0,
        "Confirmed": 1,
        "Shipped": 2,
        "Delivered": 3,
        "Cancelled": 4,
    }

    if new_status not in allowed_statuses:
        raise ValueError("Invalid order status")

    current_status = order.status

    if current_status == "Cancelled":
        raise ValueError(
            "Cancelled orders cannot change status"
        )

    if current_status == "Delivered":
        raise ValueError(
            "Delivered orders cannot change status"
        )

    if new_status == "Cancelled":
        return cancel_order(db, order)

    if new_status == current_status:
        return order

    if allowed_statuses[new_status] < allowed_statuses[current_status]:
        raise ValueError(
            "Order status can only move forward"
        )

    order.status = new_status

    if new_status == "Delivered":
        order.delivered_at = datetime.utcnow()

        # COD payment becomes paid on delivery.
        cod_payment = db.scalar(
            select(Payment).where(
                Payment.order_id == order.id,
                Payment.method == "COD",
                Payment.status == "Success",
            )
        )

        if cod_payment:
            order.payment_status = "Paid"

    db.commit()
    db.refresh(order)

    return order