from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.cart import (
    CartItemCreate,
    CartItemUpdate,
    CartResponse,
)
from app.services.cart import (
    add_item_to_cart,
    calculate_cart_subtotal,
    clear_cart,
    get_or_create_cart,
    remove_cart_item,
    update_cart_item,
)

router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)


def build_cart_response(cart):
    items = []

    for item in cart.items:
        items.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": item.product.name,
            "quantity": item.quantity,
            "price": item.product.price,
            "line_total": item.product.price * item.quantity,
        })

    return {
        "id": cart.id,
        "customer_id": cart.customer_id,
        "items": items,
        "subtotal": calculate_cart_subtotal(cart),
    }


@router.get(
    "",
    response_model=CartResponse,
)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart = get_or_create_cart(
        db,
        current_user.id,
    )

    return build_cart_response(cart)


@router.post(
    "/items",
    response_model=CartResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_cart_item(
    data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        cart = add_item_to_cart(
            db,
            current_user.id,
            data.product_id,
            data.quantity,
        )

        return build_cart_response(cart)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.put(
    "/items/{item_id}",
    response_model=CartResponse,
)
def update_cart_item_quantity(
    item_id: int,
    data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        cart = update_cart_item(
            db,
            current_user.id,
            item_id,
            data.quantity,
        )

        return build_cart_response(cart)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete(
    "/items/{item_id}",
    response_model=CartResponse,
)
def delete_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        cart = remove_cart_item(
            db,
            current_user.id,
            item_id,
        )

        return build_cart_response(cart)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    clear_cart(
        db,
        current_user.id,
    )

    return None