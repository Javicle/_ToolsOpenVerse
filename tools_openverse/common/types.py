from typing import TypeVar, Union
from uuid import UUID

from pydantic import EmailStr

from tools_openverse.common.abc.validation import AbstractValidation

T = TypeVar("T")

IdT = TypeVar("IdT", bound=Union[UUID, AbstractValidation[UUID]])
LoginT = TypeVar("LoginT", bound=Union[str, AbstractValidation[str]])
NameT = TypeVar("NameT", bound=Union[str, AbstractValidation[str]])
PasswordT = TypeVar("PasswordT", bound=Union[str, AbstractValidation[str]])
EmailT = TypeVar("EmailT", bound=Union[EmailStr, AbstractValidation[str]])


UserId = Union[UUID, AbstractValidation[UUID]]
UserLogin = Union[str, AbstractValidation[str]]
UserName = Union[str, AbstractValidation[str]]
UserPassword = Union[str, AbstractValidation[str]]
UserEmail = Union[EmailStr, str, AbstractValidation[str]]
