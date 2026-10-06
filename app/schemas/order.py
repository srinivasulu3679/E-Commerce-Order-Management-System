from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OrderStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class OrderItemCreate(BaseModel):
    product_id: int = Field(
        ...,
        gt=0
    )

    quantity: int = Field(
        ...,
        gt=0
    )


class OrderCreate(BaseModel):
    customer_name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    customer_email: EmailStr

    items: list[OrderItemCreate] = Field(
        ...,
        min_length=1
    )


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

    model_config = ConfigDict(
        from_attributes=True
    )


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    customer_email: EmailStr
    user_id: int | None
    total_amount: Decimal
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    order_items: list[OrderItemResponse] = []

    model_config = ConfigDict(
        from_attributes=True
    )