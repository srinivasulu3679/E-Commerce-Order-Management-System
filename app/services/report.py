from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product


def get_sales_report(
    db: Session,
    start_date: date,
    end_date: date,
):
    start_datetime = datetime.combine(start_date, time.min)
    end_datetime = datetime.combine(end_date, time.max)

    paid_revenue = db.scalar(
        select(func.coalesce(func.sum(Order.grand_total), 0)).where(
            Order.payment_status == "Paid",
            Order.created_at >= start_datetime,
            Order.created_at <= end_datetime,
        )
    )

    refunded_amount = db.scalar(
        select(func.coalesce(func.sum(Order.grand_total), 0)).where(
            Order.payment_status == "Refunded",
            Order.created_at >= start_datetime,
            Order.created_at <= end_datetime,
        )
    )

    total_orders = db.scalar(
        select(func.count(Order.id)).where(
            Order.created_at >= start_datetime,
            Order.created_at <= end_datetime,
        )
    )

    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_orders": int(total_orders or 0),
        "paid_revenue": Decimal(paid_revenue or 0),
        "refunded_amount": Decimal(refunded_amount or 0),
    }


def get_orders_by_status(db: Session):
    rows = db.execute(
        select(
            Order.status,
            func.count(Order.id).label("count"),
        )
        .group_by(Order.status)
        .order_by(Order.status)
    ).all()

    return [
        {
            "status": row.status,
            "count": int(row.count),
        }
        for row in rows
    ]


def get_top_products(db: Session, limit: int = 5):
    rows = db.execute(
        select(
            Product.id,
            Product.name,
            func.sum(OrderItem.quantity).label("total_quantity"),
            func.sum(OrderItem.line_total).label("total_sales"),
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, Order.id == OrderItem.order_id)
        .where(
            Order.status != "Cancelled",
            Order.payment_status == "Paid",
        )
        .group_by(Product.id, Product.name)
        .order_by(
            func.sum(OrderItem.quantity).desc()
        )
        .limit(limit)
    ).all()

    return [
        {
            "product_id": row.id,
            "product_name": row.name,
            "total_quantity": int(row.total_quantity or 0),
            "total_sales": Decimal(row.total_sales or 0),
        }
        for row in rows
    ]


def get_low_stock_products(
    db: Session,
    threshold: int = 5,
):
    return list(
        db.scalars(
            select(Product)
            .where(
                Product.stock_quantity < threshold,
                Product.is_active.is_(True),
            )
            .order_by(Product.stock_quantity.asc())
        ).all()
    )