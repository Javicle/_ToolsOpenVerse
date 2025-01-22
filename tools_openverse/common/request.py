"""
API Client for managing user and authentication requests.
Provides type-safe route management and request handling with automatic URL construction.
"""

from enum import Enum
from typing import Any, Optional, Type, Union

import httpx
from fastapi import HTTPException, status
from pydantic import BaseModel

from .config import settings
from .types import RoutesNamespaceTypes


class UsersRoutes(str, Enum):
    """Enumeration of available user service routes."""

    CREATE_USER = "/users/create"
    GET_USER_BY_ID = "/users/{id}"
    GET_USER_BY_LOGIN = "/users/login/{user_login}"
    UPDATE_USER = "/users/update"
    DELETE_USER_BY_ID = "/users/delete/{user_id}"
    DELETE_USER_BY_LOGIN = "/users/delete/login/{user_login}"
    HEALTH = "/health"


class AuthenticationRoutes(str, Enum):
    """Enumeration of available authentication service routes."""

    GET_ACCESS_TOKEN = "/auth/token"
    GET_REFRESH_TOKEN = "/auth/refresh"
    GET_USER_INFO = "/auth/user/info"


class ServiceName(str, Enum):
    """Available service names for routing."""

    USERS = "USERS"
    AUTHENTICATION = "AUTHENTICATION"


RoutesTypes = Union[UsersRoutes, AuthenticationRoutes, RoutesNamespaceTypes]


class RoutesNamespace:
    """
    Namespace for managing service routes and providing route resolution.

    Attributes:
        USERS (Type[UsersRoutes]): User service routes
        AUTHENTICATION (Type[AuthenticationRoutes]): Authentication service routes
    """

    USERS: Type[UsersRoutes] = UsersRoutes
    AUTHENTICATION: Type[AuthenticationRoutes] = AuthenticationRoutes

    @classmethod
    def get_route(
        cls,
        service: ServiceName | str,
        route_name: RoutesTypes,
        params: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Resolves and returns a route string with optional parameter substitution.

        Args:
            service: Service identifier (e.g., USERS, AUTHENTICATION)
            route_name: Route identifier, either as string or enum instance
            params: Optional parameters to substitute in the route template

        Returns:
            str: Formatted route string with parameters substituted

        Raises:
            ValueError: If service or route is not found
        """

        service_value = (
            service.value.upper() if isinstance(service, ServiceName) else service.upper()
        )
        route_service = getattr(cls, service_value, None)

        if route_service is None:
            raise ValueError(f"Unknown service: {service}")

        try:
            if isinstance(route_name, (UsersRoutes, AuthenticationRoutes)) and isinstance(
                service, ServiceName
            ):
                route = route_name.value

            else:
                route = route_service[route_name.upper()].value

        except AttributeError as e:
            raise ValueError(f"Unknown endpoint: {route_name} in service: {service}, {e}")
        except KeyError as e:
            raise ValueError(f"Unknown attribute or incorrect format: {e}")

        return route.format(**(params or {}))


class HttpMethods(str, Enum):
    """HTTP methods supported by the API client."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class BaseRequestException(HTTPException):
    """
    Custom exception for handling API request errors.

    Args:
        message: Error message
        status_code: HTTP status code
        response: Optional response data
    """

    def __init__(
        self, message: Optional[str], status_code: Optional[int], response: Optional[Any] = None
    ):
        super().__init__(
            detail=(
                message
                if message
                else f"Error occurred when trying make request: {response if response else 'None response'}"
            ),
            status_code=status_code if status_code else status.HTTP_400_BAD_REQUEST,
        )


class SetRequest:
    """
    API client for making HTTP requests to services.

    Handles URL construction, request sending, and error handling.

    Args:
        timeout: Request timeout in seconds
    """

    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout

    async def _get_url(
        self, service_name: ServiceName | str, route_name: RoutesTypes, **params: Optional[Any]
    ) -> str:
        """
        Constructs full URL for the API request.

        Args:
            service_name: Service identifier
            route_name: Route identifier
            **params: URL parameters to substitute

        Returns:
            str: Complete URL with base, port, and parameters

        Raises:
            BaseRequestException: If service or route is invalid
        """
        service_name = (
            service_name.value
            if isinstance(service_name, ServiceName)
            else getattr(RoutesNamespace, service_name)
        )
        route_name = (
            route_name
            if isinstance(route_name, UsersRoutes | AuthenticationRoutes)
            else getattr(service_name, route_name)
        )

        if params:
            route = RoutesNamespace.get_route(
                service=service_name, route_name=route_name, params=params
            )

        if not service_name and not route_name:
            raise BaseRequestException(
                message=f"Route {route_name} for service {service_name} not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        base_url = settings.BASE_URL
        if not base_url.startswith(("http://", "https://")):
            base_url = f"http://{base_url}"

        base_url = base_url.rstrip("/")
        route = route_name.lstrip("/")

        if params:
            try:
                route = route.format(**params)
            except KeyError as e:
                raise BaseRequestException(
                    message=f"Missing URL parameter: {e}", status_code=status.HTTP_400_BAD_REQUEST
                )

        final_url = (
            f"{base_url}:{settings.PORT_SERVICE}/{route}"
            if settings.PORT_SERVICE
            else f"{base_url}/{route}"
        )
        print(f"[DEBUG] Constructed URL: {final_url}")  # Debug info
        return final_url

    async def send_request(
        self,
        service_name: ServiceName,
        route_name: RoutesTypes,
        route_method: HttpMethods,
        data: Optional[BaseModel] = None,
    ) -> Any:
        """
        Sends HTTP request to the specified service endpoint.

        Args:
            service_name: Service identifier
            route_name: Route identifier
            route_method: HTTP method to use
            data: Optional request body data

        Returns:
            Any: JSON response from the API

        Raises:
            BaseRequestException: For request timeouts or failures
        """
        url = await self._get_url(service_name=service_name, route_name=route_name)
        print(f"[DEBUG] Sending {route_method.value} request to URL: {url}")  # Debug info

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=route_method.value, url=url, json=data.model_dump() if data else None
                )
                print(
                    f"[DEBUG] Response status: {response.status_code}, Response body: {response.text}"
                )  # Debug info
                return response.json()
            except httpx.TimeoutException:
                raise BaseRequestException(
                    message="Request timed out", status_code=status.HTTP_504_GATEWAY_TIMEOUT
                )
            except httpx.RequestError as e:
                raise BaseRequestException(
                    message=f"Request failed: {e}",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )


class CreateUserRequest(BaseModel):
    """Request model for user creation."""

    login: str
    name: str
    password: str
    email: str


class GetUserRequest(BaseModel):
    """Request model for user retrieval."""

    id: Optional[int]
    login: Optional[str]
    name: Optional[str]
