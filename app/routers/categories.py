from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin, get_current_user
from app.database import get_db
from app.models.category import Category
from app.models.product import Product
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    data: CategoryCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(require_admin),
):
    existing = db.scalar(
        select(Category).where(Category.name == data.name)
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category already exists",
        )

    category = Category(
        name=data.name,
        description=data.description,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@router.get(
    "/",
    response_model=list[CategoryResponse],
)
def get_categories(
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    return list(
        db.scalars(
            select(Category)
            .order_by(Category.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).all()
    )


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
)
def get_category(
    category_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(get_current_user),
):
    category = db.get(Category, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return category


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(require_admin),
):
    category = db.get(Category, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    update_data = data.model_dump(exclude_unset=True)

    if "name" in update_data:
        existing = db.scalar(
            select(Category).where(
                Category.name == update_data["name"],
                Category.id != category_id,
            )
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category already exists",
            )

    for key, value in update_data.items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)

    return category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_category(
    category_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(require_admin),
):
    category = db.get(Category, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    active_product = db.scalar(
        select(Product).where(
            Product.category_id == category_id,
            Product.is_active.is_(True),
        )
    )

    if active_product:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category cannot be deleted while it has active products",
        )

    db.delete(category)
    db.commit()

    return None
