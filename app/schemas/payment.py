from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    method: str = Field(
        ...,
        pattern="^(UPI|Card|Net Banking|COD)$"
    )


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: Decimal
    method: str
    transaction_id: str
    status: str
    created_at: object

    model_config = {"from_attributes": True}