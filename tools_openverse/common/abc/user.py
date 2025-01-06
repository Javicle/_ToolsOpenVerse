from abc import ABC, abstractmethod
from datetime import datetime
from typing import TypeVar

from pydantic import BaseModel, Field

from ..types import UserEmail, UserId, UserLogin, UserName, UserPassword

T = TypeVar("T")


class ValidationRules:
    pass


class AbstractUser(ABC, BaseModel):
    """Abstract user class"""

    id: UserId
    login: UserLogin
    name: UserName
    password: UserPassword
    email: UserEmail
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = Field(default=None)

    @abstractmethod
    def change_password(self, new_password: str) -> None:
        pass
