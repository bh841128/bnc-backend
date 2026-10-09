import random
import time

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import error, get_current_user
from app.models import CartItem, Order, OrderItem, User
from app.schemas import OrderCreateIn, OrderOut

router = APIRouter(prefix="/api/orders", tags=["orders"])


def _snapshot_name(product) -> str:
    names = product.name_i18n or {}
    return names.get("en") or names.get("zh") or names.get("id") or product.sku


@router.post("", response_model=OrderOut)
def create_order(
    body: OrderCreateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart_items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    if not cart_items:
        raise error("ORDER_INVALID_STATE", "Cart is empty", 400)

    total = 0
    for ci in cart_items:
        if not ci.product or not ci.product.is_active:
            raise error("NOT_FOUND", f"Product {ci.product_id} unavailable", 404)
        if ci.quantity > ci.product.stock:
            raise error("STOCK_INSUFFICIENT", f"Not enough stock for {ci.product.sku}", 400)
        total += ci.product.price_cents * ci.quantity

    order = Order(
        order_no=f"ORD{int(time.time())}{random.randint(100, 999)}",
        user_id=user.id,
        status="pending_payment",
        total_cents=total,
        shipping_name=body.shipping_name,
        shipping_phone=body.shipping_phone,
        shipping_address=body.shipping_address,
    )
    db.add(order)
    db.flush()

    for ci in cart_items:
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=ci.product_id,
                product_name_snapshot=_snapshot_name(ci.product),
                unit_price_cents=ci.product.price_cents,
                quantity=ci.quantity,
            )
        )
        db.delete(ci)

    db.commit()
    db.refresh(order)
    return order


@router.get("", response_model=list[OrderOut])
def list_orders(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Order)
        .filter(Order.user_id == user.id)
        .order_by(Order.id.desc())
        .all()
    )


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
    if not order:
        raise error("NOT_FOUND", "Order not found", 404)
    return order
