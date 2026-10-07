from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.review import (
    ReviewCreate,
    ReviewResponse,
    ReviewUpdate,
)
from app.services.review import (
    create_review,
    delete_review,
    get_customer_review,
    get_product_rating,
    get_product_reviews,
    update_review,
)

router = APIRouter(
    prefix="/products",
    tags=["Reviews"],
)


@router.post(
    "/{product_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_review(
    product_id: int,
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_review(
            db,
            current_user.id,
            product_id,
            data.rating,
            data.comment,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/{product_id}/reviews",
    response_model=list[ReviewResponse],
)
def list_product_reviews(
    product_id: int,
    db: Session = Depends(get_db),
):
    return get_product_reviews(
        db,
        product_id,
    )


@router.get(
    "/{product_id}/rating",
)
def product_rating(
    product_id: int,
    db: Session = Depends(get_db),
):
    average, count = get_product_rating(
        db,
        product_id,
    )

    return {
        "product_id": product_id,
        "average_rating": average,
        "review_count": count,
    }


@router.put(
    "/reviews/{review_id}",
    response_model=ReviewResponse,
)
def edit_review(
    review_id: int,
    data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = get_customer_review(
        db,
        current_user.id,
        review_id,
    )

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    return update_review(
        db,
        review,
        data.model_dump(exclude_unset=True),
    )


@router.delete(
    "/reviews/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = get_customer_review(
        db,
        current_user.id,
        review_id,
    )

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    delete_review(
        db,
        review,
    )

    return None