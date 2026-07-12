from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.security import create_access_token, hash_password, verify_password
from src.models import User
from src.schemas.auth import LoginRequest, RegisterRequest


def register_user(db: Session, payload: RegisterRequest) -> User:
    existing = db.scalar(select(User).where((User.email == payload.email) | (User.username == payload.username)))
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    user = User(email=payload.email, username=payload.username, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, payload: LoginRequest) -> tuple[str, User]:
    user = db.scalar(select(User).where(User.username == payload.username))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль")
    return create_access_token(user.username, user.id), user
