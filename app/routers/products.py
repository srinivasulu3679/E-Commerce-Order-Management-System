from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin
from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.product import (
    create_product,
    update_product,
    soft_delete_product,
)


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product_endpoint(
    data: ProductCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(require_admin),
):
    try:
        product = create_product(
            db=db,
            name=data.name,
            sku=data.sku,
            description=data.description,
            category_id=data.category_id,
            price=data.price,
            stock_quantity=data.stock_quantity,
            is_active=data.is_active,
        )
        return product
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/",
    response_model=list[ProductResponse],
)
def get_products(
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: str | None = Query(None),
    category_id: int | None = Query(None),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
):
    query = select(Product).where(Product.is_active.is_(True))

    if search:
        query = query.where(
            Product.name.ilike(f"%{search}%")
        )

    if category_id is not None:
        query = query.where(
            Product.category_id == category_id
        )

    if min_price is not None:
        query = query.where(
            Product.price >= min_price
        )

    if max_price is not None:
        query = query.where(
            Product.price <= max_price
        )

    if sort_by == "price":
        sort_column = Product.price
    elif sort_by == "name":
        sort_column = Product.name
    else:
        sort_column = Product.created_at

    if sort_order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    query = query.offset(skip).limit(limit)

    return list(db.scalars(query).all())


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product(
    product_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(get_current_user),
):
    product = db.get(Product, product_id)

    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
)
def update_product_endpoint(
    product_id: int,
    data: ProductUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(require_admin),
):
    product = db.get(Product, product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    try:
        return update_product(
            db,
            product,
            data.model_dump(exclude_unset=True),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete(
    "/{product_id}",
    response_model=ProductResponse,
)
def delete_product(
    product_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(require_admin),
):
    product = db.get(Product, product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return soft_delete_product(db, product)
