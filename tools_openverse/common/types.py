from typing import TypeAlias, TypeVar, Union
from uuid import UUID

from pydantic import EmailStr

IdT = TypeVar("IdT", bound=Union[UUID, str])
LoginT = TypeVar("LoginT", bound=str)
NameT = TypeVar("NameT", bound=str)
PasswordT = TypeVar("PasswordT", bound=str)
EmailT = TypeVar("EmailT", bound=Union[EmailStr, str])

_Id: TypeAlias = Union[str, UUID]
_Login: TypeAlias = str
_Name: TypeAlias = str
_Password: TypeAlias = str
_Email: TypeAlias = Union[str, EmailStr]

_AccessToken: TypeAlias = str
_RefreshToken: TypeAlias = str


class UserTypes:
    id = _Id
    login = _Login
    name = _Name
    password = _Password
    email = _Email


class JwtTokenTypes:
    access_token = _AccessToken
    refresh_token = _RefreshToken
