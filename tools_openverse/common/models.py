from typing import Self

from fastapi import Form
from pydantic import BaseModel


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
