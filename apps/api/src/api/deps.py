from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.core.security import decode_access_token
from src.database.session import get_db
from src.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login-form")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("user_id"))
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен")
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь недоступен")
    return user


ROLE_HIERARCHY = {"analyst": 10, "manager": 20, "admin": 30}


def require_roles(*allowed_roles: str):
    allowed = set(allowed_roles)

    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для выполнения операции",
            )
        return user

    return dependency


def require_min_role(minimum_role: str):
    minimum_level = ROLE_HIERARCHY[minimum_role]

    def dependency(user: User = Depends(get_current_user)) -> User:
        if ROLE_HIERARCHY.get(user.role, 0) < minimum_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для выполнения операции",
            )
        return user

    return dependency
