from typing import Optional, Self

from fastapi import Form
from pydantic import BaseModel


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
    def as_form(cls, login: str = Form(...), password: str = Form(...)) -> Self:  # noqa: B008
        return cls(
            login=login,
            password=password,
        )
