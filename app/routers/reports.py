from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database import get_db
from app.models.product import Product
from app.models.user import User
from app.services.report import (
    get_low_stock_products,
    get_orders_by_status,
    get_sales_report,
    get_top_products,
)

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get("/sales")
def sales_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return get_sales_report(
        db,
        start_date,
        end_date,
    )


@router.get("/orders-by-status")
def orders_by_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return get_orders_by_status(db)


@router.get("/top-products")
def top_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return get_top_products(db, limit=5)


@router.get("/low-stock")
def low_stock_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return [
        {
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "stock_quantity": product.stock_quantity,
        }
        for product in get_low_stock_products(db)
    ]