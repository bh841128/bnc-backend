from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import error
from app.models import User
from app.schemas import LoginIn, RegisterIn, TokenResponse, UserOut
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise error("UNAUTHORIZED", "Email already registered", 400)
    user = User(email=body.email, password_hash=hash_password(body.password), role="customer")
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user_id=user.id, role=user.role)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise error("UNAUTHORIZED", "Invalid credentials", 401)
    token = create_access_token(user_id=user.id, role=user.role)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))
