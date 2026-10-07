from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    order_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    address_id: Mapped[int] = mapped_column(
        ForeignKey("addresses.id"),
        nullable=False,
        index=True
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    delivery_charge: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    grand_total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="Pending",
        nullable=False,
        index=True
    )

    payment_status: Mapped[str] = mapped_column(
        String(30),
        default="Unpaid",
        nullable=False,
        index=True
    )

    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    customer = relationship(
        "User",
        back_populates="orders"
    )

    address = relationship(
        "Address",
        back_populates="orders"
    )

    order_items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    payments = relationship(
        "Payment",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    returns = relationship(
        "ReturnRequest",
        back_populates="order",
        cascade="all, delete-orphan"
    )