from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.services.product_service import (
    create_product,
    delete_product,
    get_product,
    get_products,
    update_product,
)


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product_endpoint(
    product_data: ProductCreate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    _: Annotated[
        User,
        Depends(require_admin),
    ],
):
    return create_product(
        db,
        product_data,
    )


@router.get(
    "",
    response_model=list[ProductResponse],
)
def list_products(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    _: Annotated[
        User,
        Depends(get_current_user),
    ],
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    category_id: int | None = Query(
        default=None,
        gt=0,
    ),
    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=150,
    ),
):
    return get_products(
        db=db,
        skip=skip,
        limit=limit,
        category_id=category_id,
        search=search,
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product_endpoint(
    product_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    _: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    return get_product(
        db,
        product_id,
    )


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
)
def update_product_endpoint(
    product_id: int,
    product_data: ProductUpdate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    _: Annotated[
        User,
        Depends(require_admin),
    ],
):
    return update_product(
        db,
        product_id,
        product_data,
    )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product_endpoint(
    product_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    _: Annotated[
        User,
        Depends(require_admin),
    ],
):
    delete_product(
        db,
        product_id,
    )

    return None