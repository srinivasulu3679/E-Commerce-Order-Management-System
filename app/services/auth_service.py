from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.user import UserLogin, UserRegister


def register_user(
    db: Session,
    user_data: UserRegister,
) -> User:
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(
            user_data.password
        ),
        role="customer",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    login_data: UserLogin,
) -> str:
    user = db.query(User).filter(
        User.email == login_data.email
    ).first()

    if not user or not verify_password(
        login_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role,
            "email": user.email,
        }
    )

    return access_token
