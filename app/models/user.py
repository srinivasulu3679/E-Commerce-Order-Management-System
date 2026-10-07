from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(20),
        default="customer",
        nullable=False,
        index=True
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

    # Customer -> Many Orders
    orders = relationship(
        "Order",
        back_populates="customer",
        cascade="all, delete-orphan"
    )

    # Customer -> One Cart
    cart = relationship(
        "Cart",
        back_populates="customer",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # Customer -> Many Addresses
    addresses = relationship(
        "Address",
        back_populates="customer",
        cascade="all, delete-orphan"
    )

    # Customer -> Many Reviews
    reviews = relationship(
        "Review",
        back_populates="customer",
        cascade="all, delete-orphan"
    )

    # Customer -> Many Returns
    returns = relationship(
        "ReturnRequest",
        back_populates="customer",
        cascade="all, delete-orphan"
    )