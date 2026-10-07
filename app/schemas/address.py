from pydantic import BaseModel, Field, field_validator


class AddressCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150)
    phone: str
    address_line: str = Field(..., min_length=5, max_length=300)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    pincode: str
    is_default: bool = False

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits")
        return value

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, value: str) -> str:
        if not value.isdigit() or len(value) != 6:
            raise ValueError("Pincode must contain exactly 6 digits")
        return value


class AddressUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )
    phone: str | None = None
    address_line: str | None = Field(
        default=None,
        min_length=5,
        max_length=300
    )
    city: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )
    state: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )
    pincode: str | None = None
    is_default: bool | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is not None and (
            not value.isdigit() or len(value) != 10
        ):
            raise ValueError("Phone number must contain exactly 10 digits")
        return value

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, value: str | None) -> str | None:
        if value is not None and (
            not value.isdigit() or len(value) != 6
        ):
            raise ValueError("Pincode must contain exactly 6 digits")
        return value


class AddressResponse(BaseModel):
    id: int
    customer_id: int
    full_name: str
    phone: str
    address_line: str
    city: str
    state: str
    pincode: str
    is_default: bool

    model_config = {"from_attributes": True}