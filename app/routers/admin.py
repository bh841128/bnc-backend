from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import error, require_admin
from app.models import Order, Product, User
from app.schemas import (
    DashboardOut,
    OrderOut,
    ProductAdminIn,
    ProductAdminPatch,
    ProductOut,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/dashboard", response_model=DashboardOut)
def dashboard(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    product_count = db.query(func.count(Product.id)).scalar() or 0
    order_count = db.query(func.count(Order.id)).scalar() or 0
    paid_gmv = (
        db.query(func.coalesce(func.sum(Order.total_cents), 0))
        .filter(Order.status == "paid")
        .scalar()
    )
    return DashboardOut(
        product_count=product_count,
        order_count=order_count,
        paid_gmv_cents=int(paid_gmv or 0),
    )


@router.get("/products", response_model=list[ProductOut])
def admin_list_products(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(Product).order_by(Product.id.desc()).all()


@router.post("/products", response_model=ProductOut)
def admin_create_product(
    body: ProductAdminIn,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if db.query(Product).filter(Product.sku == body.sku).first():
        raise error("ORDER_INVALID_STATE", "SKU already exists", 400)
    product = Product(**body.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/products/{product_id}", response_model=ProductOut)
def admin_get_product(
    product_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)
    if not product:
        raise error("NOT_FOUND", "Product not found", 404)
    return product


@router.patch("/products/{product_id}", response_model=ProductOut)
def admin_patch_product(
    product_id: int,
    body: ProductAdminPatch,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)
    if not product:
        raise error("NOT_FOUND", "Product not found", 404)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(product, k, v)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}")
def admin_delete_product(
    product_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)
    if not product:
        raise error("NOT_FOUND", "Product not found", 404)
    db.delete(product)
    db.commit()
    return {"ok": True}


@router.get("/orders", response_model=list[OrderOut])
def admin_list_orders(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(Order).order_by(Order.id.desc()).all()


@router.get("/orders/{order_id}", response_model=OrderOut)
def admin_get_order(
    order_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    order = db.get(Order, order_id)
    if not order:
        raise error("NOT_FOUND", "Order not found", 404)
    return order
