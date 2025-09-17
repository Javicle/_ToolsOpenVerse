"""
This module defines type aliases and Pydantic models for user authentication,
JWT tokens, and API response schemas.
It provides a shared set of types for use throughout the OpenVerse tools package.
"""

from datetime import datetime, timedelta
from typing import Any, Literal, Optional, TypeAlias, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

J = TypeVar("J", bound=BaseModel | dict[Any, Any] | str)


# Basic types
IdType: TypeAlias = Union[str, UUID]  # Unique identifier type for users and tokens
LoginType: TypeAlias = str  # User login name type
NameType: TypeAlias = str  # User display name type
PasswordType: TypeAlias = str  # User password type
EmailType: TypeAlias = Union[str, EmailStr]  # User email address type
IsActiveType: TypeAlias = bool  # Indicates if a user is active
CreatedAtType: TypeAlias = datetime  # Timestamp for creation
UpdatedAtType: TypeAlias = datetime  # Timestamp for last update
AccessTokenType: TypeAlias = str  # JWT access token string
RefreshTokenType: TypeAlias = str  # JWT refresh token string 
TokenType: TypeAlias = Optional[Literal["Bearer"]]  # Token type, usually 'Bearer'
SubType: TypeAlias = Union[NameType, UUID]  # Subject type for JWT payload
ScopesType: TypeAlias = Optional[list[str]]  # List of scopes/permissions (optional)
ExpiresType: TypeAlias = timedelta  # Expiration duration
ExpiresAtType: TypeAlias = datetime  # Expiration timestamp
JwtAlgorithmType: TypeAlias = str  # JWT algorithm name
JwtSecretKeyType: TypeAlias = str  # JWT secret key string

# Sentinal type for using instead of None
Sentinal: Any = object


class UserTypes(BaseModel):
    """
    Data model for a user.
    Represents the main user entity with authentication and profile fields.
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
    Data model for a JWT token response.
    Contains access and refresh tokens and the token type.
    """

    access_token: AccessTokenType
    refresh_token: RefreshTokenType
    token_type: TokenType


class TokenPayloadTypes(BaseModel):
    """
    Data model for the payload of a JWT token.
    Includes subject, scopes, and expiration duration.
    """

    sub: SubType
    scopes: ScopesType
    exp: ExpiresType


class DecodedTokenTypes(BaseModel):
    """
    Data model for a decoded JWT token.
    Contains the token string, algorithm, and secret key used.
    """

    token: AccessTokenType
    jwt_algorithm: JwtAlgorithmType
    jwt_secret_key: JwtSecretKeyType


class RefreshTokenTypes(BaseModel):
    """
    Data model for a refresh token entry.
    Associates a user with a refresh token and its expiration.
    """

    user_id: IdType
    refresh_token: RefreshTokenType
    expires_at: ExpiresAtType


UsersRoutesTypes = Literal[
    "CREATE_USER",  # Route for creating a new user
    "GET_USER_BY_ID",  # Route for retrieving a user by ID
    "GET_USER_BY_LOGIN",  # Route for retrieving a user by login
    "UPDATE_USER",  # Route for updating user information
    "DELETE_USER_BY_ID",  # Route for deleting a user by ID
    "DELETE_USER_BY_LOGIN",  # Route for deleting a user by login
    "HEALTH",  # Route for health check
    "LOG_IN",  # Route for user login
]

AuthenticationRoutesTypes = Literal[
    "GET_ACCESS_TOKEN",  # Route for obtaining an access token
    "GET_REFRESH_TOKEN",  # Route for obtaining a refresh token
    "GET_USER_INFO",  # Route for retrieving user info from token
]

RoutesNamespaceTypes = Union[
    UsersRoutesTypes, AuthenticationRoutesTypes
]  # All possible route types


class ErrorResponse(BaseModel):
    """
    Standard error response schema for API endpoints.
    Contains an error message and optional HTTP status code.
    """

    error: str = Field(..., description="Error message")
    status_code: Optional[int] = Field(None, description="Optional HTTP status code")


class SuccessResponse(BaseModel):
    """
    Standard success response schema for API endpoints.
    Contains a detail dictionary, success flag, and HTTP status code.
    """

    detail: dict[str, Any]
    success: bool = Field(default=True)
    status_code: int = Field(description="HTTP status code")


JSONResponseTypes = (
    SuccessResponse | ErrorResponse
)  # Union type for any API JSON response
