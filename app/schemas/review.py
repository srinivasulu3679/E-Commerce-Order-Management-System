from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = Field(
        default=None,
        max_length=1000
    )


class ReviewUpdate(BaseModel):
    rating: int | None = Field(
        default=None,
        ge=1,
        le=5
    )
    comment: str | None = Field(
        default=None,
        max_length=1000
    )


class ReviewResponse(BaseModel):
    id: int
    customer_id: int
    product_id: int
    rating: int
    comment: str | None
    created_at: object
    updated_at: object

    model_config = {
        "from_attributes": True
    }