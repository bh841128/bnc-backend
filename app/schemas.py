from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field


class ErrorBody(BaseModel):
    code: str
    message: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ProductOut(BaseModel):
    id: int
    sku: str
    price_cents: int
    stock: int
    category: str
    is_active: bool
    name_i18n: dict[str, str]
    description_i18n: dict[str, str]
    image_url: str | None = None

    class Config:
        from_attributes = True


class ProductAdminIn(BaseModel):
    sku: str
    price_cents: int
    stock: int
    category: str = "general"
    is_active: bool = True
    name_i18n: dict[str, str]
    description_i18n: dict[str, str]
    image_url: str | None = None


class ProductAdminPatch(BaseModel):
    sku: str | None = None
    price_cents: int | None = None
    stock: int | None = None
    category: str | None = None
    is_active: bool | None = None
    name_i18n: dict[str, str] | None = None
    description_i18n: dict[str, str] | None = None
    image_url: str | None = None


class CartItemIn(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)


class CartItemPatch(BaseModel):
    quantity: int = Field(ge=1)


class CartItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductOut

    class Config:
        from_attributes = True


class OrderCreateIn(BaseModel):
    shipping_name: str
    shipping_phone: str
    shipping_address: str


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    product_name_snapshot: str
    unit_price_cents: int
    quantity: int

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    order_no: str
    status: str
    total_cents: int
    shipping_name: str
    shipping_phone: str
    shipping_address: str
    created_at: datetime
    paid_at: datetime | None = None
    items: list[OrderItemOut] = []

    class Config:
        from_attributes = True


class PaymentCreateIn(BaseModel):
    order_id: int


class PaymentConfirmIn(BaseModel):
    result: Literal["succeeded", "failed"]


class PaymentOut(BaseModel):
    id: int
    payment_no: str
    order_id: int
    amount_cents: int
    status: str
    provider: str
    created_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True


class PaymentConfirmOut(BaseModel):
    payment: PaymentOut
    order: OrderOut


class DashboardOut(BaseModel):
    product_count: int
    order_count: int
    paid_gmv_cents: int


class OkAny(BaseModel):
    data: Any | None = None
