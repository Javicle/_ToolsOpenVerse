from typing import TypeVar, Union
from uuid import UUID

from pydantic import EmailStr

from tools_openverse.common.abc.validation import AbstractValidation

T = TypeVar("T")

IdT = TypeVar("IdT", UUID, AbstractValidation[UUID])
LoginT = TypeVar("LoginT", str, AbstractValidation[str])
NameT = TypeVar("NameT", str, AbstractValidation[str])
PasswordT = TypeVar("PasswordT", str, AbstractValidation[str])
EmailT = TypeVar("EmailT", str, AbstractValidation[str])


UserId = Union[UUID, AbstractValidation[UUID]]
UserLogin = Union[str, AbstractValidation[str]]
UserName = Union[str, AbstractValidation[str]]
UserPassword = Union[str, AbstractValidation[str]]
UserEmail = Union[EmailStr, str, AbstractValidation[str]]
