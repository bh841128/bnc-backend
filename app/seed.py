from sqlalchemy.orm import Session

from app.models import Product, User
from app.security import hash_password


def seed_if_empty(db: Session) -> None:
    if db.query(User).count() == 0:
        db.add_all(
            [
                User(
                    email="customer@demo.com",
                    password_hash=hash_password("demo1234"),
                    role="customer",
                ),
                User(
                    email="admin@demo.com",
                    password_hash=hash_password("admin1234"),
                    role="admin",
                ),
            ]
        )

    if db.query(Product).count() == 0:
        products = [
            Product(
                sku="BNC-TEE-01",
                price_cents=12900,
                stock=50,
                category="apparel",
                name_i18n={
                    "zh": "BNC 经典 T 恤",
                    "en": "BNC Classic Tee",
                    "id": "Kaos Klasik BNC",
                },
                description_i18n={
                    "zh": "柔软棉质，适合日常穿着。",
                    "en": "Soft cotton tee for everyday wear.",
                    "id": "Kaos katun lembut untuk sehari-hari.",
                },
                image_url=None,
            ),
            Product(
                sku="BNC-MUG-01",
                price_cents=5900,
                stock=80,
                category="home",
                name_i18n={
                    "zh": "BNC 陶瓷马克杯",
                    "en": "BNC Ceramic Mug",
                    "id": "Mug Keramik BNC",
                },
                description_i18n={
                    "zh": "350ml 陶瓷杯，耐热。",
                    "en": "350ml ceramic mug, heat-resistant.",
                    "id": "Mug keramik 350ml, tahan panas.",
                },
            ),
            Product(
                sku="BNC-BAG-01",
                price_cents=19900,
                stock=30,
                category="accessories",
                name_i18n={
                    "zh": "BNC 帆布托特包",
                    "en": "BNC Canvas Tote",
                    "id": "Tote Kanvas BNC",
                },
                description_i18n={
                    "zh": "轻便耐用，适合通勤。",
                    "en": "Light and durable for commuting.",
                    "id": "Ringan dan tahan lama untuk commuting.",
                },
            ),
            Product(
                sku="BNC-CAP-01",
                price_cents=8900,
                stock=40,
                category="accessories",
                name_i18n={
                    "zh": "BNC 棒球帽",
                    "en": "BNC Baseball Cap",
                    "id": "Topi Baseball BNC",
                },
                description_i18n={
                    "zh": "可调节帽围，透气网眼。",
                    "en": "Adjustable fit with breathable mesh.",
                    "id": "Ukuran adjustable dengan mesh breathable.",
                },
            ),
        ]
        db.add_all(products)

    db.commit()
