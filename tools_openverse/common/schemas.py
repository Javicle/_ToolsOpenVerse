from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field

from .types import UserEmail, UserID, UserLogin, UserName, UserPassword


class ValidationRules:
    pass


class AbstractUser(ABC, BaseModel):
    """Abstract user class"""

    id: UserID
    login: UserLogin
    name: UserName
    password: UserPassword
    email: EmailStr | UserEmail
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = Field(default=None)

    @abstractmethod
    def change_password(self, new_password: str) -> None:
        pass


class AbstractValidation(ABC, BaseModel):
    """Abstract Validation class for users"""

    value: Any

    # @field_validator("value")
    @classmethod
    @abstractmethod
    def validate(cls, value: Any) -> Any:
        pass

    def __str__(self) -> Any:
        return f"{self.__class__.__name__}({self.value})"
