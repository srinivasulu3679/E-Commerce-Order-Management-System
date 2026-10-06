from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def create_product(
    db: Session,
    product_data: ProductCreate,
) -> Product:
    category = db.query(Category).filter(
        Category.id == product_data.category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock_quantity=product_data.stock_quantity,
        category_id=product_data.category_id,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def get_product(
    db: Session,
    product_id: int,
) -> Product:
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    category_id: int | None = None,
    search: str | None = None,
) -> list[Product]:
    query = db.query(Product)

    if category_id is not None:
        query = query.filter(
            Product.category_id == category_id
        )

    if search:
        query = query.filter(
            Product.name.ilike(
                f"%{search}%"
            )
        )

    return (
        query
        .order_by(Product.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_product(
    db: Session,
    product_id: int,
    product_data: ProductUpdate,
) -> Product:
    product = get_product(
        db,
        product_id,
    )

    update_data = product_data.model_dump(
        exclude_unset=True
    )

    if "category_id" in update_data:
        category = db.query(Category).filter(
            Category.id == update_data["category_id"]
        ).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

    for field, value in update_data.items():
        setattr(
            product,
            field,
            value,
        )

    db.commit()
    db.refresh(product)

    return product


def delete_product(
    db: Session,
    product_id: int,
) -> None:
    product = get_product(
        db,
        product_id,
    )

    if product.order_items:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product cannot be deleted because it is used in existing orders",
        )

    db.delete(product)
    db.commit()