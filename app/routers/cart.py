from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import error, get_current_user
from app.models import CartItem, Product, User
from app.schemas import CartItemIn, CartItemOut, CartItemPatch

router = APIRouter(prefix="/api/cart", tags=["cart"])


def _item_out(item: CartItem) -> CartItemOut:
    return CartItemOut(
        id=item.id,
        product_id=item.product_id,
        quantity=item.quantity,
        product=item.product,
    )


@router.get("/items", response_model=list[CartItemOut])
def list_cart(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = (
        db.query(CartItem)
        .filter(CartItem.user_id == user.id)
        .order_by(CartItem.id.asc())
        .all()
    )
    return [_item_out(i) for i in items]


@router.post("/items", response_model=CartItemOut)
def add_cart_item(
    body: CartItemIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.get(Product, body.product_id)
    if not product or not product.is_active:
        raise error("NOT_FOUND", "Product not found", 404)
    if body.quantity > product.stock:
        raise error("STOCK_INSUFFICIENT", "Not enough stock", 400)

    item = (
        db.query(CartItem)
        .filter(CartItem.user_id == user.id, CartItem.product_id == body.product_id)
        .first()
    )
    if item:
        new_qty = item.quantity + body.quantity
        if new_qty > product.stock:
            raise error("STOCK_INSUFFICIENT", "Not enough stock", 400)
        item.quantity = new_qty
    else:
        item = CartItem(user_id=user.id, product_id=body.product_id, quantity=body.quantity)
        db.add(item)
    db.commit()
    db.refresh(item)
    return _item_out(item)


@router.patch("/items/{item_id}", response_model=CartItemOut)
def patch_cart_item(
    item_id: int,
    body: CartItemPatch,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == user.id).first()
    if not item:
        raise error("NOT_FOUND", "Cart item not found", 404)
    if body.quantity > item.product.stock:
        raise error("STOCK_INSUFFICIENT", "Not enough stock", 400)
    item.quantity = body.quantity
    db.commit()
    db.refresh(item)
    return _item_out(item)


@router.delete("/items/{item_id}")
def delete_cart_item(
    item_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == user.id).first()
    if not item:
        raise error("NOT_FOUND", "Cart item not found", 404)
    db.delete(item)
    db.commit()
    return {"ok": True}
