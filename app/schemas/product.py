from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    sku: str = Field(..., min_length=2, max_length=100)
    description: str | None = None
    category_id: int = Field(..., gt=0)
    price: Decimal = Field(..., gt=0)
    stock_quantity: int = Field(..., ge=0)
    is_active: bool = True


class ProductUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )
    sku: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )
    description: str | None = None
    category_id: int | None = Field(
        default=None,
        gt=0
    )
    price: Decimal | None = Field(
        default=None,
        gt=0
    )
    stock_quantity: int | None = Field(
        default=None,
        ge=0
    )
    is_active: bool | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    description: str | None
    category_id: int
    price: Decimal
    stock_quantity: int
    is_active: bool
    average_rating: float = 0.0
    review_count: int = 0
    created_at: object
    updated_at: object

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    skip: int
    limit: int