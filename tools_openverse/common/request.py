"""
API Client for managing user and authentication requests.
Provides type-safe route management and request
handling with automatic URL construction.
"""

from enum import Enum
from typing import Any, Optional, Type, Union

import httpx
from fastapi import HTTPException, status
from pydantic import BaseModel

from .config import settings
from .logger_ import setup_logger
from .types import (
    ErrorResponse,
    JSONResponseTypes,
    RoutesNamespaceTypes,
    SuccessResponse,
)

logger = setup_logger()


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

    LOG_IN = "/auth/user/log_in"
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
        logger.debug(
            "Getting route for service=%s, route_name=%s, params=%s",
            service,
            route_name,
            params,
        )

        service_value = (
            service.value.upper()
            if isinstance(service, ServiceName)
            else str(service).upper()
        )
        route_service = getattr(cls, service_value, None)

        if route_service is None:
            logger.error("Unknown service: %s", service)
            raise ValueError(f"Unknown service: {service}")

        try:
            if isinstance(route_name, (UsersRoutes, AuthenticationRoutes)):
                route = str(route_name.value)
            else:
                # route_name may be a string key of the enum
                route = str(route_service[route_name].value)

            logger.debug("Base route template: %s", route)

            if "{" in route and "}" in route:
                if not params:
                    logger.error("Missing parameters for route template: %s", route)
                    raise ValueError("Missing parameters for route")

                logger.debug("Formatting route with parameters: %s", params)
                route = route.format(**params)

            logger.info("Resolved route: %s", route)
            return route

        except AttributeError as exc:
            logger.error(
                "Unknown endpoint: %s in service: %s. Error: %s",
                route_name,
                service,
                exc,
            )
            raise ValueError(
                f"Unknown endpoint: {route_name} in service: {service}, {exc}"
            ) from exc
        except KeyError as exc:
            logger.error("Unknown attribute or incorrect format: %s", exc)
            raise ValueError(f"Unknown attribute or incorrect format: {exc}") from exc


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
    """

    def __init__(
        self,
        message: Optional[str],
        status_code: Optional[int],
        response: Optional[Any] = None,
    ):
        # Correctly build error_detail string
        if message:
            error_detail = message
        else:
            error_detail = f"Error occurred when trying make request: {
                response if response else 'None response'}"

        logger.error(
            "BaseRequestException raised: status_code=%s, message=%s, response=%s",
            status_code,
            message,
            response,
        )

        super().__init__(
            detail=error_detail,
            status_code=status_code if status_code else status.HTTP_400_BAD_REQUEST,
        )


class SetRequest:
    """
    API client for making HTTP requests to services.
    Handles URL construction, request sending, and error handling.
    """

    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        logger.info("SetRequest initialized with timeout: %s seconds", timeout)

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    @staticmethod
    async def validate_http_method(
        route_name: RoutesTypes, route_method: HttpMethods
    ) -> None:
        """
        Validates if the given HTTP method is allowed for the specified route.
        """
        logger.debug("Validating HTTP method %s for route %s", route_method, route_name)

        try:
            # get route key name (like CREATE_USER)
            if isinstance(route_name, (UsersRoutes, AuthenticationRoutes)):
                route_name_str = route_name.name
            else:
                # if route_name passed as string key already
                route_name_str = str(route_name)

            expected_method = getattr(_HttpRoutesMethods, route_name_str).value
            if expected_method != route_method.value:
                logger.error(
                    "HTTP method validation failed: got %s, expected %s for route %s",
                    route_method.value,
                    expected_method,
                    route_name_str,
                )
                # format a simple message
                raise ValueError(
                    f"Invalid HTTP method {
                        route_method.value
                    } for route {route_name_str}. Expected: {expected_method}"
                )

            logger.debug("HTTP method validation passed")

        except AttributeError as exc:
            logger.error("Route not found in _HttpRoutesMethods: %s", route_name)
            raise ValueError(
                f"Route {route_name} not found in _HttpRoutesMethods"
            ) from exc

    async def _get_url(
        self,
        service_name: ServiceName | str,
        route_name: RoutesTypes,
        params: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Constructs full URL for the API request.
        """
        logger.debug(
            "Constructing URL for service=%s, route=%s, params=%s",
            service_name,
            route_name,
            params,
        )

        try:
            service_value = (
                service_name.value
                if isinstance(service_name, ServiceName)
                else str(service_name).upper()
            )

            # Resolve route (may raise ValueError)
            route = RoutesNamespace.get_route(
                service=service_value, route_name=route_name, params=params
            )

            if not route.startswith("/"):
                route = "/" + route

        except Exception as exc:
            logger.error("Failed to get route: %s", exc)
            raise BaseRequestException(
                message=(
                f"Failed to get route for service {service_name}, route {route_name}"
                ),
                status_code=status.HTTP_404_NOT_FOUND,
            ) from exc

        # build base url
        base_url = settings.BASE_URL
        if not base_url.startswith(("http://", "https://")):
            base_url = f"http://{base_url}"
        base_url = base_url.rstrip("/")

        try:
            service_name_for_port = (
                service_name.value
                if isinstance(service_name, ServiceName)
                else str(service_name).upper()
            )
            service_port: str | int = getattr(
                ServicesPorts, service_name_for_port
            ).value
            logger.debug(
                "Found service port: %s for service: %s",
                service_port,
                service_name_for_port,
            )
        except AttributeError as exc:
            logger.error("Service port not found for service: %s", service_name)
            raise BaseRequestException(
                message=f"Service port not found for service {service_name}",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            ) from exc

        if service_port:
            final_url = f"{base_url}:{service_port}{route}"
        else:
            final_url = f"{base_url}{route}"

        logger.info("Constructed final URL: %s", final_url)
        return final_url

    async def send_request(
        self,
        service_name: ServiceName,
        route_name: RoutesTypes,
        route_method: HttpMethods,
        request_data: BaseModel | None = None,
        form_data: bool = False,
        extra_params: dict[str, Any] | None = None,
        url_params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> JSONResponseTypes:
        """
        Sends HTTP request to the specified service endpoint.
        """
        logger.info(
            "Sending %s request to service=%s, route=%s, form_data=%s",
            route_method.value,
            service_name.value if hasattr(service_name, "value") else service_name,
            route_name,
            form_data,
        )

        if request_data:
            logger.debug("Request data provided: %s", type(request_data).__name__)

        await self.validate_http_method(
            route_name=route_name, route_method=route_method
        )

        # Build url with parameters
        url = await self._get_url(
            service_name=service_name,
            route_name=route_name,
            params=url_params,
        )

        # Init vars for different types
        json_data = None
        form_data_dict = None
        query_params: dict[str, Any] | None = None

        # Get data if request_data
        req_json = request_data.model_dump(exclude_none=True) if request_data else None

        # preparation data for some methods
        if route_method.value in ["POST", "PUT", "PATCH"] and req_json:
            if form_data:
                form_data_dict = req_json
            else:
                json_data = req_json

        # preparation query data
        if route_method.value == "GET":
            query_params = {}
            if req_json:
                query_params.update(req_json)
            if extra_params:
                query_params.update(extra_params)
            if not query_params:
                query_params = None
        elif extra_params:
            query_params = extra_params

        client = await self._ensure_client()
        try:
            logger.debug("Making HTTP request to: %s", url)
            logger.debug("Query params: %s", query_params)
            logger.debug("JSON data: %s", json_data)
            logger.debug("Form data: %s", form_data_dict)

            response = await client.request(
                method=route_method.value,
                url=url,
                json=json_data,
                data=form_data_dict,
                params=query_params,
                headers=headers,
            )

            logger.info("Received response with status code: %s", response.status_code)

            # parsing json response
            try:
                result = response.json()
                logger.debug("Response JSON parsed successfully")
            except Exception as e:
                logger.error("Failed to parse response JSON: %s", e)
                raise BaseRequestException(
                    message=f"Failed to parse response JSON: {e}",
                    status_code=response.status_code,
                    response=response.text,
                ) from e

            # checking status response
            if response.status_code >= 400:
                error_message = (
                    result.get("detail", f"HTTP {response.status_code} error")
                    if isinstance(result, dict)
                    else str(result)
                )
                logger.warning(
                    "API returned error response: status_code=%s, detail=%s",
                    response.status_code,
                    error_message,
                )
                return ErrorResponse(
                    error=error_message, status_code=response.status_code
                )

            # Good response
            logger.info("Request completed successfully")
            return SuccessResponse(
                detail=result, success=True, status_code=response.status_code
            )

        except httpx.TimeoutException as e:
            logger.error("Request timed out after %s seconds: %s", self.timeout, e)
            raise BaseRequestException(
                message=f"Request timed out: {e}",
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            ) from e

        except httpx.RequestError as e:
            logger.error("Request failed: %s", e)
            raise BaseRequestException(
                message=f"Request failed: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from e

        except Exception as e:
            logger.error("Unexpected error occurred: %s", e)
            raise BaseRequestException(
                message=f"Unexpected error: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from e
