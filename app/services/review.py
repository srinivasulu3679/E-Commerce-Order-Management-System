from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.review import Review


def create_review(
    db: Session,
    customer_id: int,
    product_id: int,
    rating: int,
    comment: str | None,
) -> Review:
    if rating < 1 or rating > 5:
        raise ValueError("Rating must be between 1 and 5")

    product = db.get(Product, product_id)

    if not product:
        raise ValueError("Product not found")

    # Customer must have a delivered order containing this product.
    delivered_order = db.scalar(
        select(Order)
        .join(OrderItem, OrderItem.order_id == Order.id)
        .where(
            Order.customer_id == customer_id,
            Order.status == "Delivered",
            OrderItem.product_id == product_id,
        )
    )

    if not delivered_order:
        raise ValueError(
            "You can review a product only after receiving it"
        )

    existing_review = db.scalar(
        select(Review).where(
            Review.customer_id == customer_id,
            Review.product_id == product_id,
        )
    )

    if existing_review:
        raise ValueError(
            "You have already reviewed this product"
        )

    review = Review(
        customer_id=customer_id,
        product_id=product_id,
        rating=rating,
        comment=comment,
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


def get_product_reviews(
    db: Session,
    product_id: int,
) -> list[Review]:
    return list(
        db.scalars(
            select(Review)
            .where(Review.product_id == product_id)
            .order_by(Review.created_at.desc())
        ).all()
    )


def get_customer_review(
    db: Session,
    customer_id: int,
    review_id: int,
) -> Review | None:
    return db.scalar(
        select(Review).where(
            Review.id == review_id,
            Review.customer_id == customer_id,
        )
    )


def update_review(
    db: Session,
    review: Review,
    data: dict,
) -> Review:
    for key, value in data.items():
        setattr(review, key, value)

    db.commit()
    db.refresh(review)

    return review


def delete_review(
    db: Session,
    review: Review,
) -> None:
    db.delete(review)
    db.commit()


def get_product_rating(
    db: Session,
    product_id: int,
) -> tuple[float, int]:
    result = db.execute(
        select(
            func.avg(Review.rating),
            func.count(Review.id),
        ).where(
            Review.product_id == product_id
        )
    ).one()

    average = float(result[0] or 0)
    count = int(result[1] or 0)

    return round(average, 2), count