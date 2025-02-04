from abc import ABC, abstractmethod

from pydantic import BaseModel

from tools_openverse.common.types import (
    CreatedAtType,
    EmailType,
    IdType,
    IsActiveType,
    LoginType,
    NameType,
    PasswordType,
    UpdatedAtType,
)


class AbstractUser(ABC, BaseModel):
    """Abstract user class"""

    id: IdType
    login: LoginType
    name: NameType
    password: PasswordType
    email: EmailType
    is_active: IsActiveType
    created_at: CreatedAtType
    updated_at: UpdatedAtType

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True

    @abstractmethod
    def change_password(self, new_password: str) -> None:
        pass
