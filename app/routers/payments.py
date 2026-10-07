from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services.payment import get_order_payments, process_payment


router = APIRouter(
    prefix="/orders",
    tags=["Payments"],
)


@router.post(
    "/{order_id}/pay",
    response_model=PaymentResponse,
)
def pay_order(
    order_id: int,
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return process_payment(
            db,
            order_id,
            current_user.id,
            data.method,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/{order_id}/payments",
    response_model=list[PaymentResponse],
)
def get_payments(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_order_payments(
            db,
            order_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )