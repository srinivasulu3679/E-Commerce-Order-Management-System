from fastapi import FastAPI

from app.routers import (
    auth,
    categories,
    products,
    orders,
    cart,
    address,
    payments,
    returns,
    reviews,
    reports,
)


app = FastAPI(
    title="E-Commerce Order Management API",
    description=(
        "A complete FastAPI backend for managing "
        "products, carts, orders, payments, returns, "
        "refunds, reviews, and email notifications."
    ),
    version="1.0.0",
)


app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(cart.router)
app.include_router(address.router)
app.include_router(payments.router)
app.include_router(returns.router)
app.include_router(reviews.router)
app.include_router(reports.router)


@app.get(
    "/",
    tags=["Health Check"],
)
def root():
    return {
        "message": "E-Commerce Order Management API is running",
        "status": "success",
    }


@app.get(
    "/health",
    tags=["Health Check"],
)
def health_check():
    return {
        "status": "healthy",
        "service": "ecommerce-order-management",
    }