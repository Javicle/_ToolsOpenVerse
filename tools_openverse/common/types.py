from typing import TypeVar, Union
from uuid import UUID

from pydantic import EmailStr

IdT = TypeVar("IdT", bound=Union[UUID, str])
LoginT = TypeVar("LoginT", bound=str)
NameT = TypeVar("NameT", bound=str)
PasswordT = TypeVar("PasswordT", bound=str)
EmailT = TypeVar("EmailT", bound=Union[EmailStr, str])
