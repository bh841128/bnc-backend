import random
import time
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import error, get_current_user
from app.models import Order, Payment, Product, User
from app.schemas import PaymentConfirmIn, PaymentConfirmOut, PaymentCreateIn, PaymentOut

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.post("/mock", response_model=PaymentOut)
def create_mock_payment(
    body: PaymentCreateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == body.order_id, Order.user_id == user.id).first()
    if not order:
        raise error("NOT_FOUND", "Order not found", 404)
    if order.status != "pending_payment":
        raise error("ORDER_INVALID_STATE", "Order is not pending payment", 409)

    payment = Payment(
        payment_no=f"PAY{int(time.time())}{random.randint(100, 999)}",
        order_id=order.id,
        amount_cents=order.total_cents,
        status="pending",
        provider="mock",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.post("/mock/{payment_id}/confirm", response_model=PaymentConfirmOut)
def confirm_mock_payment(
    payment_id: int,
    body: PaymentConfirmIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payment = db.get(Payment, payment_id)
    if not payment:
        raise error("NOT_FOUND", "Payment not found", 404)
    order = db.get(Order, payment.order_id)
    if not order or order.user_id != user.id:
        raise error("FORBIDDEN", "Not your payment", 403)
    if payment.status != "pending" or order.status != "pending_payment":
        raise error("PAYMENT_INVALID_STATE", "Payment already finalized", 409)

    if body.result == "failed":
        payment.status = "failed"
        payment.completed_at = datetime.utcnow()
        order.status = "cancelled"
        db.commit()
        db.refresh(payment)
        db.refresh(order)
        return PaymentConfirmOut(payment=payment, order=order)

    # succeeded
    for item in order.items:
        product = db.get(Product, item.product_id)
        if not product or product.stock < item.quantity:
            raise error("STOCK_INSUFFICIENT", "Not enough stock at pay time", 400)
    for item in order.items:
        product = db.get(Product, item.product_id)
        product.stock -= item.quantity

    payment.status = "succeeded"
    payment.completed_at = datetime.utcnow()
    order.status = "paid"
    order.paid_at = datetime.utcnow()
    db.commit()
    db.refresh(payment)
    db.refresh(order)
    return PaymentConfirmOut(payment=payment, order=order)
