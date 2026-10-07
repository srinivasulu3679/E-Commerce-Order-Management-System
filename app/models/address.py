from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    phone: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    address_line: Mapped[str] = mapped_column(
        String(300),
        nullable=False
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    state: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    pincode: Mapped[str] = mapped_column(
        String(6),
        nullable=False
    )

    is_default: Mapped[bool] = mapped_column(
        default=False,
        nullable=False
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
        back_populates="addresses"
    )

    orders = relationship(
        "Order",
        back_populates="address"
    )