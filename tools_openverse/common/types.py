from typing import Union
from uuid import UUID
from .schemas import AbstractValidation
from pydantic import EmailStr

from typing_extensions import Protocol, TypeVar

T = TypeVar("T")

class HasValue(Protocol[T]):
    value: T


BaseUserID = UUID
BaseUserLogin = str
BaseUserName = str
BaseUserPassword = str
BaseUserEmail = EmailStr


UserId = Union[BaseUserID, HasValue[BaseUserID]]
UserLogin = Union[BaseUserLogin, HasValue[BaseUserLogin]]
UserName = Union[BaseUserName, HasValue[BaseUserName]]
UserPassword = Union[BaseUserPassword, HasValue[BaseUserPassword]]
UserEmail = Union[EmailStr, BaseUserEmail, HasValue[BaseUserEmail]]
