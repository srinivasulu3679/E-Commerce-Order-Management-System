from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin
from app.database import get_db
from app.models.category import Category
from app.models.user import User
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    category_data: CategoryCreate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    _: Annotated[
        User,
        Depends(require_admin),
    ],
):
    existing_category = db.query(Category).filter(
        Category.name == category_data.name
    ).first()

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category already exists",
        )

    category = Category(
        name=category_data.name,
        description=category_data.description,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@router.get(
    "",
    response_model=list[CategoryResponse],
)
def list_categories(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    _: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    return (
        db.query(Category)
        .order_by(Category.name.asc())
        .all()
    )


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
)
def get_category(
    category_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    _: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

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
    category_data: CategoryUpdate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    _: Annotated[
        User,
        Depends(require_admin),
    ],
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    update_data = category_data.model_dump(
        exclude_unset=True
    )

    if "name" in update_data:
        existing_category = (
            db.query(Category)
            .filter(
                Category.name == update_data["name"],
                Category.id != category_id,
            )
            .first()
        )

        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category name already exists",
            )

    for field, value in update_data.items():
        setattr(
            category,
            field,
            value,
        )

    db.commit()
    db.refresh(category)

    return category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_category(
    category_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    _: Annotated[
        User,
        Depends(require_admin),
    ],
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    if category.products:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category cannot be deleted because it contains products",
        )

    db.delete(category)
    db.commit()

    return None