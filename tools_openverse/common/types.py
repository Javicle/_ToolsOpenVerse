from datetime import datetime, timedelta
from typing import Any, Literal, Optional, TypeAlias, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

J = TypeVar("J", bound=BaseModel | dict[Any, Any] | str)

# Basic types
IdType: TypeAlias = Union[str, UUID]
LoginType: TypeAlias = str
NameType: TypeAlias = str
PasswordType: TypeAlias = str
EmailType: TypeAlias = Union[str, EmailStr]
IsActiveType: TypeAlias = bool
CreatedAtType: TypeAlias = datetime
UpdatedAtType: TypeAlias = datetime
AccessTokenType: TypeAlias = str
RefreshTokenType: TypeAlias = Optional[str]
TokenTypeType: TypeAlias = Optional[Literal["Bearer"]]
SubType: TypeAlias = Union[NameType, UUID]
ScopesType: TypeAlias = Optional[list[str]]
ExpiresType: TypeAlias = timedelta
ExpiresAtType: TypeAlias = datetime
JwtAlgorithmType: TypeAlias = str
JwtSecretKeyType: TypeAlias = str


class UserTypes(BaseModel):
    """
    Модель данных для пользователя.
    """

    id: IdType
    login: LoginType
    name: NameType
    password: PasswordType
    email: EmailType
    is_active: IsActiveType
    created_at: CreatedAtType
    updated_at: UpdatedAtType


class JwtTokenTypes(BaseModel):
    """
    Модель данных для JWT-токена.
    """

    access_token: AccessTokenType
    refresh_token: RefreshTokenType
    token_type: TokenTypeType


class TokenPayloadTypes(BaseModel):
    """
    Модель данных для полезной нагрузки токена.
    """

    sub: SubType
    scopes: ScopesType
    exp: ExpiresType


class DecodedTokenTypes(BaseModel):
    """
    Модель данных для декодированного токена.
    """

    token: AccessTokenType
    jwt_algorithm: JwtAlgorithmType
    jwt_secret_key: JwtSecretKeyType


class RefreshTokenTypes(BaseModel):
    """
    Модель данных для обновления токена.
    """

    user_id: IdType
    refresh_token: RefreshTokenType
    expires_at: ExpiresAtType


UsersRoutesTypes = Literal[
    "CREATE_USER",
    "GET_USER_BY_ID",
    "GET_USER_BY_LOGIN",
    "UPDATE_USER",
    "DELETE_USER_BY_ID",
    "DELETE_USER_BY_LOGIN",
    "HEALTH",
    "LOG_IN",
]

AuthenticationRoutesTypes = Literal["GET_ACCESS_TOKEN", "GET_REFRESH_TOKEN", "GET_USER_INFO"]

RoutesNamespaceTypes = Union[UsersRoutesTypes, AuthenticationRoutesTypes]


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    status_code: Optional[int] = Field(None, description="Optional HTTP status code")


class SuccessResponse(BaseModel):
    detail: dict[str, Any]
    success: bool = Field(default=True)
    status_code: int = Field(description="HTTP status code")


JSONResponseTypes = SuccessResponse | ErrorResponse
