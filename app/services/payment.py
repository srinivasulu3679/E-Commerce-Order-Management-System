
import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.payment import Payment


VALID_PAYMENT_METHODS = {
    "UPI",
    "Card",
    "Net Banking",
    "COD",
}


def process_payment(
    db: Session,
    order: Order,
    method: str,
    amount: Decimal,
) -> Payment:

    if method not in VALID_PAYMENT_METHODS:
        raise ValueError("Invalid payment method")

    if order.status == "Cancelled":
        raise ValueError("Cancelled orders cannot be paid")

    if order.payment_status == "Paid":
        raise ValueError("Order has already been paid")

    if amount != order.grand_total:
        raise ValueError("Payment amount must match order total")

    transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"

    payment = Payment(
        order_id=order.id,
        amount=amount,
        method=method,
        transaction_id=transaction_id,
        status="Success",
    )

    db.add(payment)

    if method == "COD":
        # COD is paid when the order is delivered.
        order.status = "Confirmed"
        order.payment_status = "Unpaid"
    else:
        order.status = "Confirmed"
        order.payment_status = "Paid"

    db.commit()
    db.refresh(payment)

    return payment


def get_order_payments(
    db: Session,
    order: Order,
) -> list[Payment]:

    return list(
        db.scalars(
            select(Payment)
            .where(Payment.order_id == order.id)
            .order_by(Payment.created_at.desc())
        ).all()
    )
