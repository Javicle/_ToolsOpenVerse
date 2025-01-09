from abc import ABC, abstractmethod

from pydantic import BaseModel

from tools_openverse.common.types import UserTypes


class AbstractUser(ABC, BaseModel):
    """Abstract user class"""

    id: UserTypes.id
    login: UserTypes.login
    name: UserTypes.name
    password: UserTypes.password
    email: UserTypes.email
    is_active: UserTypes.is_active
    created_at: UserTypes.created_at
    updated_at: UserTypes.updated_at

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True

    @abstractmethod
    def change_password(self, new_password: str) -> None:
        pass
