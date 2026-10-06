from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    description: str | None = Field(
        default=None,
        max_length=2000
    )

    price: Decimal = Field(
        ...,
        gt=0
    )

    stock_quantity: int = Field(
        ...,
        ge=0
    )

    category_id: int = Field(
        ...,
        gt=0
    )


class ProductUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    description: str | None = Field(
        default=None,
        max_length=2000
    )

    price: Decimal | None = Field(
        default=None,
        gt=0
    )

    stock_quantity: int | None = Field(
        default=None,
        ge=0
    )

    category_id: int | None = Field(
        default=None,
        gt=0
    )


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    stock_quantity: int
    category_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )