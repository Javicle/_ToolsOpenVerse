from typing import TypeVar, Union
from uuid import UUID

from pydantic import EmailStr

from tools_openverse.common.abc.validation import AbstractValidation

T = TypeVar("T")

BaseUserID = UUID
BaseUserLogin = str
BaseUserName = str
BaseUserPassword = str
BaseUserEmail = EmailStr

UserId = Union[BaseUserID, AbstractValidation[BaseUserID]]
UserLogin = Union[BaseUserLogin, AbstractValidation[BaseUserLogin]]
UserName = Union[BaseUserName, AbstractValidation[BaseUserName]]
UserPassword = Union[BaseUserPassword, AbstractValidation[BaseUserPassword]]
UserEmail = Union[EmailStr, BaseUserEmail, AbstractValidation[BaseUserEmail]]
