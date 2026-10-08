
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.order import Order
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services.payment import get_order_payments, process_payment
from app.utils.email import send_email


router = APIRouter(prefix="/orders", tags=["Payments"])


@router.post("/{order_id}/pay", response_model=PaymentResponse)
def pay_order(
    order_id: int,
    data: PaymentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.scalar(
        select(Order).where(
            Order.id == order_id,
            Order.customer_id == current_user.id,
        )
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    try:
        payment = process_payment(
            db,
            order,
            data.method,
            order.grand_total,
        )

        background_tasks.add_task(
            send_email,
            current_user.email,
            "Payment Successful",
            f"Hello {current_user.name},\n\n"
            f"Payment for order {order.order_number} was successful.\n"
            f"Payment Method: {payment.method}\n"
            f"Amount: {payment.amount}\n"
            f"Transaction ID: {payment.transaction_id}\n\n"
            "Thank you for your purchase.",
        )

        return payment

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get("/{order_id}/payments", response_model=list[PaymentResponse])
def get_payments(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.scalar(
        select(Order).where(
            Order.id == order_id,
            Order.customer_id == current_user.id,
        )
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return get_order_payments(db, order)
