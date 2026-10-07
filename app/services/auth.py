from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import hash_password, verify_password
from app.models.user import User


def register_user(
    db: Session,
    name: str,
    email: str,
    password: str,
) -> User:
    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        raise ValueError("Email already registered")

    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role="customer",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:
    user = db.scalar(
        select(User).where(User.email == email)
    )

    if not user:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user