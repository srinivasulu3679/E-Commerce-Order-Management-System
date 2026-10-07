from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.payment import Payment
from app.models.product import Product
from app.models.return_request import ReturnRequest


def create_return_request(
    db: Session,
    order: Order,
    customer_id: int,
    reason: str,
) -> ReturnRequest:
    if order.customer_id != customer_id:
        raise ValueError("You can only return your own orders")

    if order.status != "Delivered":
        raise ValueError(
            "Returns are allowed only for delivered orders"
        )

    if not order.delivered_at:
        raise ValueError(
            "Delivery date is not available"
        )

    if datetime.utcnow() > order.delivered_at + timedelta(days=7):
        raise ValueError(
            "Return window has expired. Returns are allowed within 7 days"
        )

    existing_return = db.scalar(
        select(ReturnRequest).where(
            ReturnRequest.order_id == order.id
        )
    )

    if existing_return:
        raise ValueError(
            "A return request already exists for this order"
        )

    return_request = ReturnRequest(
        order_id=order.id,
        customer_id=customer_id,
        reason=reason,
        status="Pending",
    )

    db.add(return_request)
    db.commit()
    db.refresh(return_request)

    return return_request


def get_customer_returns(
    db: Session,
    customer_id: int,
) -> list[ReturnRequest]:
    return list(
        db.scalars(
            select(ReturnRequest)
            .where(
                ReturnRequest.customer_id == customer_id
            )
            .order_by(ReturnRequest.created_at.desc())
        ).all()
    )


def approve_return(
    db: Session,
    return_request: ReturnRequest,
) -> ReturnRequest:
    if return_request.status != "Pending":
        raise ValueError(
            "Only pending returns can be approved"
        )

    order = db.get(Order, return_request.order_id)

    if not order:
        raise ValueError("Order not found")

    try:
        # Restore stock for every item in the returned order.
        for item in order.order_items:
            product = db.scalar(
                select(Product)
                .where(Product.id == item.product_id)
                .with_for_update()
            )

            if product:
                product.stock_quantity += item.quantity

        refund_amount = Decimal(str(order.grand_total))

        return_request.status = "Approved"
        return_request.refund_amount = refund_amount

        order.payment_status = "Refunded"

        # Mark the order as refunded/cancelled after approval.
        order.status = "Cancelled"

        # Update successful payment records to refunded.
        payments = db.scalars(
            select(Payment).where(
                Payment.order_id == order.id,
                Payment.status == "Success",
            )
        ).all()

        for payment in payments:
            payment.status = "Refunded"

        db.commit()
        db.refresh(return_request)

        return return_request

    except Exception:
        db.rollback()
        raise


def reject_return(
    db: Session,
    return_request: ReturnRequest,
    rejection_reason: str,
) -> ReturnRequest:
    if return_request.status != "Pending":
        raise ValueError(
            "Only pending returns can be rejected"
        )

    return_request.status = "Rejected"
    return_request.rejection_reason = rejection_reason

    db.commit()
    db.refresh(return_request)

    return return_request