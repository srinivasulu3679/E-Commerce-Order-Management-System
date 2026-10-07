from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product


def create_product(
    db: Session,
    name: str,
    sku: str,
    description: str | None,
    category_id: int,
    price,
    stock_quantity: int,
    is_active: bool = True,
) -> Product:
    existing_sku = db.scalar(
        select(Product).where(Product.sku == sku)
    )

    if existing_sku:
        raise ValueError("SKU already exists")

    category = db.get(Category, category_id)

    if not category:
        raise ValueError("Category not found")

    product = Product(
        name=name,
        sku=sku,
        description=description,
        category_id=category_id,
        price=price,
        stock_quantity=stock_quantity,
        is_active=is_active,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def update_product(
    db: Session,
    product: Product,
    data: dict,
) -> Product:
    if "sku" in data and data["sku"] != product.sku:
        existing_sku = db.scalar(
            select(Product).where(
                Product.sku == data["sku"],
                Product.id != product.id,
            )
        )

        if existing_sku:
            raise ValueError("SKU already exists")

    if "category_id" in data:
        category = db.get(Category, data["category_id"])

        if not category:
            raise ValueError("Category not found")

    for key, value in data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)

    return product


def soft_delete_product(
    db: Session,
    product: Product,
) -> Product:
    product.is_active = False

    db.commit()
    db.refresh(product)

    return product