from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.address import AddressCreate, AddressResponse, AddressUpdate
from app.services.address import (
    create_address,
    delete_address,
    get_customer_addresses,
    set_default_address,
    update_address,
)

router = APIRouter(
    prefix="/addresses",
    tags=["Addresses"],
)


@router.post(
    "",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_address(
    data: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_address(
            db,
            current_user.id,
            data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[AddressResponse],
)
def get_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_customer_addresses(
        db,
        current_user.id,
    )


@router.put(
    "/{address_id}",
    response_model=AddressResponse,
)
def update_customer_address(
    address_id: int,
    data: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return update_address(
            db,
            current_user.id,
            address_id,
            data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.delete(
    "/{address_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_customer_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        delete_address(
            db,
            current_user.id,
            address_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    return None


@router.put(
    "/{address_id}/default",
    response_model=AddressResponse,
)
def make_default_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return set_default_address(
            db,
            current_user.id,
            address_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )