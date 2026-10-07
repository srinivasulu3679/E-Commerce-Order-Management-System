"""create ecommerce order management tables

Revision ID: ea0532b44b28
Revises: 527288df4e4d
Create Date: 2026-10-07 17:04:49.378040

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision: str = "ea0532b44b28"
down_revision: Union[str, Sequence[str], None] = "527288df4e4d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "addresses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("phone", sa.String(length=10), nullable=False),
        sa.Column("address_line", sa.String(length=300), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=False),
        sa.Column("pincode", sa.String(length=6), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_addresses_customer_id"),
        "addresses",
        ["customer_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_addresses_id"),
        "addresses",
        ["id"],
        unique=False,
    )

    op.create_table(
        "carts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_carts_customer_id"),
        "carts",
        ["customer_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_carts_id"),
        "carts",
        ["id"],
        unique=False,
    )

    op.create_table(
        "cart_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cart_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cart_id"],
            ["carts.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "cart_id",
            "product_id",
            name="uq_cart_product",
        ),
    )

    op.create_index(
        op.f("ix_cart_items_cart_id"),
        "cart_items",
        ["cart_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_cart_items_id"),
        "cart_items",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_cart_items_product_id"),
        "cart_items",
        ["product_id"],
        unique=False,
    )

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "customer_id",
            "product_id",
            name="uq_customer_product_review",
        ),
    )

    op.create_index(
        op.f("ix_reviews_customer_id"),
        "reviews",
        ["customer_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_reviews_id"),
        "reviews",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_reviews_product_id"),
        "reviews",
        ["product_id"],
        unique=False,
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column(
            "amount",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.Column("method", sa.String(length=30), nullable=False),
        sa.Column(
            "transaction_id",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_payments_id"),
        "payments",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_payments_order_id"),
        "payments",
        ["order_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_payments_transaction_id"),
        "payments",
        ["transaction_id"],
        unique=True,
    )

    op.create_table(
        "returns",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column(
            "refund_amount",
            sa.Numeric(precision=12, scale=2),
            nullable=True,
        ),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_returns_customer_id"),
        "returns",
        ["customer_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_returns_id"),
        "returns",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_returns_order_id"),
        "returns",
        ["order_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_returns_status"),
        "returns",
        ["status"],
        unique=False,
    )

    op.add_column(
        "order_items",
        sa.Column(
            "line_total",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
    )

    op.drop_column("order_items", "subtotal")

    op.add_column(
        "orders",
        sa.Column(
            "order_number",
            sa.String(length=50),
            nullable=False,
        ),
    )
    op.add_column(
        "orders",
        sa.Column(
            "customer_id",
            sa.Integer(),
            nullable=False,
        ),
    )
    op.add_column(
        "orders",
        sa.Column(
            "address_id",
            sa.Integer(),
            nullable=False,
        ),
    )
    op.add_column(
        "orders",
        sa.Column(
            "subtotal",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
    )
    op.add_column(
        "orders",
        sa.Column(
            "tax_amount",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
    )
    op.add_column(
        "orders",
        sa.Column(
            "delivery_charge",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
    )
    op.add_column(
        "orders",
        sa.Column(
            "grand_total",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
    )
    op.add_column(
        "orders",
        sa.Column(
            "payment_status",
            sa.String(length=30),
            nullable=False,
        ),
    )
    op.add_column(
        "orders",
        sa.Column(
            "delivered_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    # Remove old foreign key BEFORE dropping its supporting index.
    op.drop_constraint(
        op.f("orders_ibfk_1"),
        "orders",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_orders_customer_email"),
        table_name="orders",
    )
    op.drop_index(
        op.f("ix_orders_user_id"),
        table_name="orders",
    )

    op.create_index(
        op.f("ix_orders_address_id"),
        "orders",
        ["address_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_orders_customer_id"),
        "orders",
        ["customer_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_orders_order_number"),
        "orders",
        ["order_number"],
        unique=True,
    )
    op.create_index(
        op.f("ix_orders_payment_status"),
        "orders",
        ["payment_status"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_orders_address_id",
        "orders",
        "addresses",
        ["address_id"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_orders_customer_id",
        "orders",
        "users",
        ["customer_id"],
        ["id"],
    )

    op.drop_column("orders", "customer_name")
    op.drop_column("orders", "user_id")
    op.drop_column("orders", "total_amount")
    op.drop_column("orders", "customer_email")

    op.add_column(
        "products",
        sa.Column(
            "sku",
            sa.String(length=100),
            nullable=False,
        ),
    )
    op.add_column(
        "products",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
        ),
    )

    op.create_index(
        op.f("ix_products_is_active"),
        "products",
        ["is_active"],
        unique=False,
    )
    op.create_index(
        op.f("ix_products_sku"),
        "products",
        ["sku"],
        unique=True,
    )

    op.create_index(
        op.f("ix_users_role"),
        "users",
        ["role"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_users_role"),
        table_name="users",
    )

    op.drop_index(
        op.f("ix_products_sku"),
        table_name="products",
    )
    op.drop_index(
        op.f("ix_products_is_active"),
        table_name="products",
    )

    op.drop_column("products", "is_active")
    op.drop_column("products", "sku")

    op.add_column(
        "orders",
        sa.Column(
            "customer_email",
            mysql.VARCHAR(length=150),
            nullable=False,
        ),
    )
    op.add_column(
        "orders",
        sa.Column(
            "total_amount",
            mysql.DECIMAL(precision=12, scale=2),
            nullable=False,
        ),
    )
    op.add_column(
        "orders",
        sa.Column(
            "user_id",
            mysql.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "orders",
        sa.Column(
            "customer_name",
            mysql.VARCHAR(length=150),
            nullable=False,
        ),
    )

    op.drop_constraint(
        "fk_orders_customer_id",
        "orders",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_orders_address_id",
        "orders",
        type_="foreignkey",
    )

    op.create_foreign_key(
        op.f("orders_ibfk_1"),
        "orders",
        "users",
        ["user_id"],
        ["id"],
    )

    op.drop_index(
        op.f("ix_orders_payment_status"),
        table_name="orders",
    )
    op.drop_index(
        op.f("ix_orders_order_number"),
        table_name="orders",
    )
    op.drop_index(
        op.f("ix_orders_customer_id"),
        table_name="orders",
    )
    op.drop_index(
        op.f("ix_orders_address_id"),
        table_name="orders",
    )

    op.create_index(
        op.f("ix_orders_user_id"),
        "orders",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_orders_customer_email"),
        "orders",
        ["customer_email"],
        unique=False,
    )

    op.drop_column("orders", "delivered_at")
    op.drop_column("orders", "payment_status")
    op.drop_column("orders", "grand_total")
    op.drop_column("orders", "delivery_charge")
    op.drop_column("orders", "tax_amount")
    op.drop_column("orders", "subtotal")
    op.drop_column("orders", "address_id")
    op.drop_column("orders", "customer_id")
    op.drop_column("orders", "order_number")

    op.add_column(
        "order_items",
        sa.Column(
            "subtotal",
            mysql.DECIMAL(precision=12, scale=2),
            nullable=False,
        ),
    )
    op.drop_column("order_items", "line_total")

    op.drop_index(
        op.f("ix_returns_status"),
        table_name="returns",
    )
    op.drop_index(
        op.f("ix_returns_order_id"),
        table_name="returns",
    )
    op.drop_index(
        op.f("ix_returns_id"),
        table_name="returns",
    )
    op.drop_index(
        op.f("ix_returns_customer_id"),
        table_name="returns",
    )
    op.drop_table("returns")

    op.drop_index(
        op.f("ix_payments_transaction_id"),
        table_name="payments",
    )
    op.drop_index(
        op.f("ix_payments_order_id"),
        table_name="payments",
    )
    op.drop_index(
        op.f("ix_payments_id"),
        table_name="payments",
    )
    op.drop_table("payments")

    op.drop_index(
        op.f("ix_reviews_product_id"),
        table_name="reviews",
    )
    op.drop_index(
        op.f("ix_reviews_id"),
        table_name="reviews",
    )
    op.drop_index(
        op.f("ix_reviews_customer_id"),
        table_name="reviews",
    )
    op.drop_table("reviews")

    op.drop_index(
        op.f("ix_cart_items_product_id"),
        table_name="cart_items",
    )
    op.drop_index(
        op.f("ix_cart_items_id"),
        table_name="cart_items",
    )
    op.drop_index(
        op.f("ix_cart_items_cart_id"),
        table_name="cart_items",
    )
    op.drop_table("cart_items")

    op.drop_index(
        op.f("ix_carts_id"),
        table_name="carts",
    )
    op.drop_index(
        op.f("ix_carts_customer_id"),
        table_name="carts",
    )
    op.drop_table("carts")

    op.drop_index(
        op.f("ix_addresses_id"),
        table_name="addresses",
    )
    op.drop_index(
        op.f("ix_addresses_customer_id"),
        table_name="addresses",
    )
    op.drop_table("addresses")