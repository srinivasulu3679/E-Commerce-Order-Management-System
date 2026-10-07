from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.user import User


def get_or_create_cart(
    db: Session,
    customer_id: int,
) -> Cart:
    cart = db.scalar(
        select(Cart).where(Cart.customer_id == customer_id)
    )

    if cart:
        return cart

    cart = Cart(customer_id=customer_id)

    db.add(cart)
    db.commit()
    db.refresh(cart)

    return cart


def add_item_to_cart(
    db: Session,
    customer_id: int,
    product_id: int,
    quantity: int,
) -> Cart:
    if quantity < 1:
        raise ValueError("Quantity must be at least 1")

    product = db.get(Product, product_id)

    if not product:
        raise ValueError("Product not found")

    if not product.is_active:
        raise ValueError("Inactive products cannot be added to cart")

    cart = get_or_create_cart(db, customer_id)

    item = db.scalar(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id,
        )
    )

    if item:
        new_quantity = item.quantity + quantity

        if new_quantity > product.stock_quantity:
            raise ValueError(
                f"Only {product.stock_quantity} items are available"
            )

        item.quantity = new_quantity
    else:
        if quantity > product.stock_quantity:
            raise ValueError(
                f"Only {product.stock_quantity} items are available"
            )

        item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity,
        )

        db.add(item)

    db.commit()
    db.refresh(cart)

    return cart


def update_cart_item(
    db: Session,
    customer_id: int,
    item_id: int,
    quantity: int,
) -> Cart:
    if quantity < 1:
        raise ValueError("Quantity must be at least 1")

    cart = db.scalar(
        select(Cart).where(Cart.customer_id == customer_id)
    )

    if not cart:
        raise ValueError("Cart not found")

    item = db.scalar(
        select(CartItem).where(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id,
        )
    )

    if not item:
        raise ValueError("Cart item not found")

    product = db.get(Product, item.product_id)

    if not product or not product.is_active:
        raise ValueError("Product is not available")

    if quantity > product.stock_quantity:
        raise ValueError(
            f"Only {product.stock_quantity} items are available"
        )

    item.quantity = quantity

    db.commit()
    db.refresh(cart)

    return cart


def remove_cart_item(
    db: Session,
    customer_id: int,
    item_id: int,
) -> Cart:
    cart = db.scalar(
        select(Cart).where(Cart.customer_id == customer_id)
    )

    if not cart:
        raise ValueError("Cart not found")

    item = db.scalar(
        select(CartItem).where(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id,
        )
    )

    if not item:
        raise ValueError("Cart item not found")

    db.delete(item)
    db.commit()
    db.refresh(cart)

    return cart


def clear_cart(
    db: Session,
    customer_id: int,
) -> None:
    cart = db.scalar(
        select(Cart).where(Cart.customer_id == customer_id)
    )

    if not cart:
        return

    for item in list(cart.items):
        db.delete(item)

    db.commit()


def calculate_cart_subtotal(cart: Cart) -> Decimal:
    subtotal = Decimal("0.00")

    for item in cart.items:
        subtotal += (
            item.product.price * item.quantity
        )

    return subtotal