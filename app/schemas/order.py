from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    line_total: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    address_id: int = Field(..., gt=0)


class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_id: int
    address_id: int
    subtotal: Decimal
    tax_amount: Decimal
    delivery_charge: Decimal
    grand_total: Decimal
    status: str
    payment_status: str
    delivered_at: object | None
    created_at: object
    updated_at: object
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    status: str = Field(
        ...,
        pattern="^(Pending|Confirmed|Shipped|Delivered|Cancelled)$"
    )