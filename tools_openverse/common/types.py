from typing import TypeVar, Union
from uuid import UUID

from pydantic import EmailStr

from tools_openverse.common.abc.validation import AbstractValidation

T = TypeVar("T")

UserId = Union[UUID, AbstractValidation[UUID]]
UserLogin = Union[str, AbstractValidation[str]]
UserName = Union[str, AbstractValidation[str]]
UserPassword = Union[str, AbstractValidation[str]]
UserEmail = Union[EmailStr, str, AbstractValidation[str]]
