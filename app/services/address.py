from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.address import Address


def create_address(
    db: Session,
    customer_id: int,
    data,
) -> Address:
    data = data.model_dump()

    if data.get("is_default", False):
        db.query(Address).filter(
            Address.customer_id == customer_id
        ).update(
            {"is_default": False},
            synchronize_session=False,
        )

    address = Address(
        customer_id=customer_id,
        **data,
    )

    db.add(address)
    db.commit()
    db.refresh(address)

    return address


def get_customer_addresses(
    db: Session,
    customer_id: int,
) -> list[Address]:
    return list(
        db.scalars(
            select(Address)
            .where(Address.customer_id == customer_id)
            .order_by(Address.id.desc())
        ).all()
    )


def get_customer_address(
    db: Session,
    customer_id: int,
    address_id: int,
) -> Address | None:
    return db.scalar(
        select(Address).where(
            Address.id == address_id,
            Address.customer_id == customer_id,
        )
    )


def update_address(
    db: Session,
    address: Address,
    data,
) -> Address:
    data = data.model_dump(exclude_unset=True)

    if data.get("is_default", False):
        db.query(Address).filter(
            Address.customer_id == address.customer_id,
            Address.id != address.id,
        ).update(
            {"is_default": False},
            synchronize_session=False,
        )

    for key, value in data.items():
        setattr(address, key, value)

    db.commit()
    db.refresh(address)

    return address


def delete_address(
    db: Session,
    address: Address,
) -> None:
    db.delete(address)
    db.commit()


def set_default_address(
    db: Session,
    address: Address,
) -> Address:
    db.query(Address).filter(
        Address.customer_id == address.customer_id
    ).update(
        {"is_default": False},
        synchronize_session=False,
    )

    address.is_default = True

    db.commit()
    db.refresh(address)

    return address