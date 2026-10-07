from decimal import Decimal

from pydantic import BaseModel, Field


class ReturnCreate(BaseModel):
    reason: str = Field(..., min_length=5, max_length=1000)


class ReturnReject(BaseModel):
    rejection_reason: str = Field(..., min_length=5, max_length=1000)


class ReturnResponse(BaseModel):
    id: int
    order_id: int
    customer_id: int
    reason: str
    status: str
    refund_amount: Decimal | None
    rejection_reason: str | None
    created_at: object
    updated_at: object

    model_config = {"from_attributes": True}