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
from .types import (
    ErrorResponse,
    JSONResponseTypes,
    RoutesNamespaceTypes,
    SuccessResponse,
)


class UsersRoutes(str, Enum):
    """Enumeration of available user service routes."""

    CREATE_USER = "/users/create"
    GET_USER_BY_ID = "/users/get/{id}"
    GET_USER_BY_LOGIN = "/users/login/{user_login}"
    UPDATE_USER = "/users/update"
    DELETE_USER_BY_ID = "/users/delete/{user_id}"
    DELETE_USER_BY_LOGIN = "/users/delete/login/{user_login}"
    LOG_IN = "/users/log_in"
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


class _HttpRoutesMethods(str, Enum):
    CREATE_USER = "POST"
    GET_USER_BY_ID = "GET"
    GET_USER_BY_LOGIN = "GET"
    UPDATE_USER = "PUT"
    DELETE_USER_BY_ID = "DELETE"
    DELETE_USER_BY_LOGIN = "DELETE"
    HEALTH = "GET"
    LOG_IN = "POST"

    GET_ACCESS_TOKEN = "GET"
    GET_REFRESH_TOKEN = "GET"
    GET_USER_INFO = "GET"


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

        print("[DEBUG] Сработал метод get_route")  # Debug info
        service_value = (
            service.value.upper() if isinstance(service, ServiceName) else service.upper()
        )
        route_service = getattr(cls, service_value, None)

        if route_service is None:
            raise ValueError(f"Unknown service: {service}")

        try:
            if isinstance(route_name, (UsersRoutes, AuthenticationRoutes)):

                route = str(route_name.value)

            else:
                route = str(route_service[route_name].value)

            if "{" in route and "}" in route:
                if not params:
                    raise ValueError("Missing parameters for route")
                print(f"КОНЕЧНАЯ ССЫЛКА:  {route.format(**params)}")  # debug print
                route = route.format(**params)
            print(f"ВОТ КОНЕЧНАЯ ССЫЛКА {route}")
            return route

        except AttributeError as e:
            raise ValueError(f"Unknown endpoint: {route_name} in service: {service}, {e}") from e
        except KeyError as e:
            raise ValueError(f"Unknown attribute or incorrect format: {e}") from e

        return route.format(**params if params else {})


class HttpMethods(str, Enum):
    """HTTP methods supported by the API client."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class ServicesPorts(str, Enum):
    """Available service ports for routing."""

    USERS = settings.PORT_SERVICE_USERS
    AUTHENTICATION = settings.PORT_SERVICE_AUTH


class BaseRequestException(HTTPException):
    """
    Custom exception for handling API request errors.

    Args:
        message: Error message
        status_code: HTTP status code
        response: Optional response data
    """

    def __init__(
        self,
        message: Optional[str],
        status_code: Optional[int],
        response: Optional[Any] = None,
    ):
        super().__init__(
            detail=(
                message
                if message
                else f"Error occurred when trying make request: {
                    response if response else 'None response'}"
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

    @staticmethod
    async def validate_http_method(route_name: RoutesTypes, route_method: HttpMethods) -> None:
        """
        Validates if the given HTTP method is allowed for the specified route.

        Args:
            route_name: The route to validate.
            route_method: The HTTP method to check.

        Raises:
            ValueError: If the method does not match the expected value.
        """
        try:
            route_name_str = (  # CREATE_USER
                route_name.name
                if isinstance(route_name, UsersRoutes | AuthenticationRoutes)
                else route_name
            )

            expected_method = getattr(_HttpRoutesMethods, route_name_str).value
            if expected_method != route_method.value:
                raise ValueError(
                    f"Invalid HTTP method {route_method.value} for route {
                        route_name_str.value if isinstance(
                            route_name_str, UsersRoutes | AuthenticationRoutes)
                        else route_name_str}. "
                    f"Expected: {expected_method}"
                )
        except KeyError as e:
            raise ValueError(
                f"Route {route_name.value if isinstance(
                    route_name, UsersRoutes | AuthenticationRoutes)
                    else route_name} not found in _HttpRoutesMethods"
            ) from e

    async def _get_url(
        self,
        service_name: ServiceName | str,
        route_name: RoutesTypes,
        params: dict[str, Any] | None,
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
        route = None

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
        else:
            route = route_name.lstrip("/")

        if not service_name and not route_name:
            raise BaseRequestException(
                message=f"Route {route_name} for service {service_name} not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        base_url = settings.BASE_URL
        if not base_url.startswith(("http://", "https://")):
            base_url = f"http://{base_url}"

        base_url = base_url.rstrip("/")

        service_port: str | int = getattr(ServicesPorts, service_name).value

        if service_port:
            print(f"[DEBUG] Service port: {service_port}")  # Debug info
            final_url = (
                f"{base_url}:{service_port}{route}" if service_port else f"{base_url}/{route}"
            )
            print(f"[DEBUG] Constructed URL: {final_url}")  # Debug info
            return final_url

        raise BaseRequestException(
            message=f"Service port not found for service {service_name}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    async def send_request(  # noqa:
        self,
        service_name: ServiceName,
        route_name: RoutesTypes,
        route_method: HttpMethods,
        request_data: Optional[BaseModel] = None,
        form_data: bool = False,
    ) -> JSONResponseTypes:
        """
        Sends HTTP request to the specified service endpoint.

        Args:
            service_name: Service identifier use ServiceName
            route_name: Route identifier use UsersRoutes | AuthenticationRoutes
            route_method: HTTP method to use, use HttpMethods
            data: Optional request body data

        Returns:
            Any: JSON response from the API

        Raises:
            BaseRequestException: For request timeouts or failures
        """

        await self.validate_http_method(route_name=route_name, route_method=route_method)

        url = await self._get_url(
            service_name=service_name,
            route_name=route_name,
            params=request_data.model_dump(exclude_none=True) if request_data else None,
        )

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=route_method.value,
                    url=url,
                    json=(
                        request_data.model_dump(exclude_none=True)
                        if route_method.value in ["POST", "PUT", "PATCH"]
                        and request_data
                        and not form_data
                        else None
                    ),
                    data=(
                        request_data.model_dump(exclude_none=True)
                        if route_method.value in ["POST", "PUT", "PATCH"]
                        and request_data
                        and form_data
                        else None
                    ),
                )

                result = response.json()

                if "detail" in result and result["detail"]:
                    print("-" * 100)
                    print(f"Вот response.json : {result}")
                    print("-" * 100)
                    return ErrorResponse(error=result["detail"], status_code=response.status_code)

                if "detail" not in result:
                    return SuccessResponse(
                        detail=result, success=True, status_code=response.status_code
                    )

            except httpx.TimeoutException as e:
                raise BaseRequestException(
                    message=f"Request timed out : {e}",
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                ) from e

            except httpx.RequestError as e:
                raise BaseRequestException(
                    message=f"Request failed: {e}",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                ) from e

            return ErrorResponse(
                error="Unexpected error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
