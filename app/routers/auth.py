from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    TokenResponse,
    UserRegister,
    UserResponse,
)
from app.schemas.user import UserLogin
from app.services.auth_service import (
    authenticate_user,
    register_user,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserRegister,
    db: Annotated[Session, Depends(get_db)],
):
    return register_user(db, user_data)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends()
    ],
    db: Annotated[Session, Depends(get_db)],
):
    login_data = UserLogin(
        email=form_data.username,
        password=form_data.password,
    )

    access_token = authenticate_user(
        db,
        login_data,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    return current_user