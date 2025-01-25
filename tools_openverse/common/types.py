from datetime import datetime, timedelta
from typing import Any, Literal, Optional, TypeAlias, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

J = TypeVar("J", bound=BaseModel | dict[Any, Any] | str)

Id: TypeAlias = Union[str, UUID]
Login: TypeAlias = str
Name: TypeAlias = str
Password: TypeAlias = str
Email: TypeAlias = Union[str, EmailStr]
Is_active: TypeAlias = bool
Created_at: TypeAlias = datetime
Updated_at: TypeAlias = datetime
AccessToken: TypeAlias = str
RefreshTokenStr: TypeAlias = Optional[str]
TokenType: TypeAlias = Optional[Literal["Bearer"]]
Sub: TypeAlias = Union[Name, UUID]
Scopes: TypeAlias = Optional[list[str]]
Expires: TypeAlias = timedelta
Expires_at: TypeAlias = datetime
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
    refresh_token = RefreshTokenStr
    token_type = TokenType


class TokenPayloadTypes:
    sub = Sub
    scopes = Scopes
    exp = Expires


class DecodedTokenTypes:
    token = AccessToken
    jwt_algoritm = JwtAlgoritm
    jwt_secret_key = JwtSecretKey


class RefreshTokenTypes:
    user_id: Id
    refresh_token: RefreshTokenStr
    expires_at: Expires_at


UsersRoutesTypes = Literal[
    "CREATE_USER",
    "GET_USER_BY_ID",
    "GET_USER_BY_LOGIN",
    "UPDATE_USER",
    "DELETE_USER_BY_ID",
    "DELETE_USER_BY_LOGIN",
    "HEALTH",
]

AuthenticationRoutesTypes = Literal["GET_ACCESS_TOKEN", "GET_REFRESH_TOKEN", "GET_USER_INFO"]

RoutesNamespaceTypes = Union[UsersRoutesTypes, AuthenticationRoutesTypes]


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    status_code: Optional[int] = Field(None, description="Optional HTTP status code")


class SuccessResponse(BaseModel):
    detail: dict[str, Any]
    success: bool = Field(default=True)


JSONResponseTypes = SuccessResponse | ErrorResponse
