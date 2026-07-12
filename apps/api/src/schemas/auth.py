from pydantic import BaseModel, EmailStr, Field

from src.schemas.common import ORMModel


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=72)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(ORMModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    role: str
