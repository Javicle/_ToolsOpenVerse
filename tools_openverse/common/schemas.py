from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, TypeVar, Generic

from pydantic import BaseModel, EmailStr, Field

from .types import UserEmail, UserID, UserLogin, UserName, UserPassword

T = TypeVar("T")

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


class AbstractValidation(ABC, BaseModel, Generic[T]):
    """Abstract Validation class for users"""

    value: T

    # @field_validator("value")
    @classmethod
    @abstractmethod
    def validate(cls, value: T) -> T:
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"
