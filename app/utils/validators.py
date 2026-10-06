from decimal import Decimal


def validate_positive_price(price: Decimal) -> Decimal:
    if price <= 0:
        raise ValueError("Price must be greater than 0")

    return price


def validate_non_negative_stock(stock_quantity: int) -> int:
    if stock_quantity < 0:
        raise ValueError("Stock quantity cannot be negative")

    return stock_quantity


def validate_positive_quantity(quantity: int) -> int:
    if quantity <= 0:
        raise ValueError("Quantity must be greater than 0")

    return quantity