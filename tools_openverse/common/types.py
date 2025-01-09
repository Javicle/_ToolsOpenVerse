from datetime import datetime, timedelta
from typing import Literal, Optional, TypeAlias, Union
from uuid import UUID

from pydantic import EmailStr

Id: TypeAlias = Union[str, UUID]
Login: TypeAlias = str
Name: TypeAlias = str
Password: TypeAlias = str
Email: TypeAlias = Union[str, EmailStr]
Is_active: TypeAlias = bool
Created_at: TypeAlias = datetime
Updated_at: TypeAlias = datetime
AccessToken: TypeAlias = str
RefreshToken: TypeAlias = Optional[str]
TokenType: TypeAlias = Optional[Literal["Bearer"]]
Sub: TypeAlias = Union[str, UUID]
Scopes: TypeAlias = Optional[list[str]]
Expires: TypeAlias = timedelta
JwtAlgoritm: TypeAlias = str
JwtSecretKey: TypeAlias = str


class UserTypes:
    id = Id
    login = Login
    name = Name
    password = Password
    email = Email
    is_active = Is_active
    created_at = Created_at
    updated_at = Updated_at


class JwtTokenTypes:
    access_token = AccessToken
    refresh_token = RefreshToken
    token_type = TokenType


class TokenPayloadTypes:
    sub = Sub
    scopes = Scopes
    exp = Expires


class DecodedTokenTypes:
    token = AccessToken
    jwt_algoritm = JwtAlgoritm
    jwt_secret_key = JwtSecretKey
