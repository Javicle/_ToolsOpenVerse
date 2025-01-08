from abc import ABC, abstractmethod
from datetime import datetime
from typing import TypeVar
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from tools_openverse.common.abc.validation import AbstractValidation

T = TypeVar("T")


class ValidationRules:
    pass


class AbstractUser(ABC, BaseModel):
    """Abstract user class"""

    id: UUID | AbstractValidation[UUID]
    login: str | AbstractValidation[str]
    name: str | AbstractValidation[str]
    password: str | AbstractValidation[str]
    email: EmailStr | str | AbstractValidation[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    def change_password(self, new_password: str) -> None:
        pass
