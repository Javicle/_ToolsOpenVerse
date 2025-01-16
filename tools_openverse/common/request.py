from enum import Enum
from typing import Any, Optional

import httpx
from fastapi import HTTPException, status
from pydantic import BaseModel

from .config import settings


class ServiceName(str, Enum):
    USERS = "USERS"
    AUTHENTICATION = "AUTHENTICATION"


class HttpMethods(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class BaseRequestException(HTTPException):
    def __init__(
        self, message: Optional[str], status_code: Optional[int], response: Optional[Any] = None
    ):
        super().__init__(
            detail=(
                message
                if message
                else f"Error occurred when trying make request: {response if response else "None response"}"
            ),
            status_code=status_code if status_code else status.HTTP_400_BAD_REQUEST,
        )


class SetRequest:
    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout
        self.routes: dict[str, dict[str, str]] = {
            ServiceName.USERS.value: {
                "create_user": "/users/create",
                "get_user_by_id": "/users/{id}",
                "get_user_by_login": "/users/{user_id}",
                "update_user": "/users/update",
                "delete_user_by_id": "/users/delete/{user_id}",
                "delete_user_by_login": "/users/delete/login/{user_login}",
                "health": "/health",
            },
        }

    async def _get_url(
        self, service_name: ServiceName, route_name: str, **params: Optional[Any]
    ) -> str:
        if not self.routes[service_name]:
            raise BaseRequestException(
                message=f"Service {service_name} not found", status_code=status.HTTP_404_NOT_FOUND
            )
        if not self.routes[service_name][route_name]:
            raise BaseRequestException(
                message=f"Route {route_name} not found for service {service_name}",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        base_url = settings.BASE_URL
        if not base_url.startswith(("http://", "https://")):
            base_url = f"http://{base_url}"

        base_url = base_url.rstrip("/")
        route = self.routes[service_name][route_name].lstrip("/")

        if params:
            try:
                route = route.format(**params)
            except KeyError as e:
                raise BaseRequestException(
                    message=f"Missing URL parameter: {e}", status_code=status.HTTP_400_BAD_REQUEST
                )

        # Собираем финальный URL
        if settings.PORT_SERVICE:
            return f"{base_url}:{settings.PORT_SERVICE}/{route}"
        return f"{base_url}/{route}"

    async def send_request(
        self,
        service_name: ServiceName,
        route_name: str,
        route_method: HttpMethods,
        data: Optional[BaseModel] = None,
    ) -> Any:

        url = await self._get_url(service_name=service_name, route_name=route_name)
        print(f"Для откладки {url}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                print(
                    f"Для откладки Route_{route_method.value} , URL : {url} , DATA: {data.model_dump() if data else None}"
                )

                response = await client.request(
                    method=route_method.value, url=url, json=data.model_dump() if data else None
                )

                # response.raise_for_status()
                print(f"Для откладки {response.json}")

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
    login: str
    name: str
    password: str
    email: str


class GetUserRequest(BaseModel):
    id: Optional[int]
    login: Optional[str]
    name: Optional[str]
