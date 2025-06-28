from typing import Optional, Self

from fastapi import Form
from pydantic import BaseModel

_LOGIN_FORM = Form(...)
_PASSWORD_FORM = Form(...)


class CreateUserRequest(BaseModel):
    """Request model for user creation."""

    login: str
    name: str
    password: str
    email: str


class GetUserRequest(BaseModel):
    """Request model for user retrieval."""

    id: Optional[int | str] = None
    login: Optional[str] = None
    name: Optional[str] = None


class LoginModel(BaseModel):
    """Login request model."""

    login: str
    password: str


class LoginOAuth2PasswordRequestForm(BaseModel):
    """
    Custom form for login
    """

    login: str
    password: str

    @classmethod
    def as_form(cls, login: str = _LOGIN_FORM, password: str = _PASSWORD_FORM) -> Self:
        return cls(
            login=login,
            password=password,
        )
