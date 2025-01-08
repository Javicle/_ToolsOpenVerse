from abc import ABC, abstractmethod
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, EmailStr, Field

from tools_openverse.common.types import EmailT, IdT, LoginT, NameT, PasswordT

T = TypeVar("T")


class ValidationRules:
    pass


class AbstractUser(ABC, BaseModel, Generic[IdT, LoginT, NameT, PasswordT, EmailT]):
    """Abstract user class"""

    id: IdT
    login: LoginT
    name: NameT
    password: PasswordT
    email: EmailT | EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    def change_password(self, new_password: str) -> None:
        pass
