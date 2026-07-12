from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.database.session import get_db
from src.models import User
from src.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from src.services.audit_service import write_audit_log
from src.services.auth_service import login_user, register_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return register_user(db, payload)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    token, user = login_user(db, payload)
    write_audit_log(db, action="auth.login", user=user, request=request, entity_type="user", entity_id=user.id)
    return TokenResponse(access_token=token)


@router.post("/login-form", response_model=TokenResponse)
def login_form(request: Request, form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    token, user = login_user(db, LoginRequest(username=form.username, password=form.password))
    write_audit_log(db, action="auth.login", user=user, request=request, entity_type="user", entity_id=user.id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return user
