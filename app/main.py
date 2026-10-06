from fastapi import FastAPI

from app.routers import (
    auth_router,
    categories_router,
    products_router,
    orders_router,
)


app = FastAPI(
    title="E-Commerce Order Management API",
    description=(
        "A professional FastAPI backend for managing "
        "users, categories, products, and customer orders."
    ),
    version="1.0.0",
)


app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(orders_router)


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