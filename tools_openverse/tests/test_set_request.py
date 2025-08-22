from typing import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import TimeoutException

from tools_openverse import (
    BaseRequestException,
    ErrorResponse,
    HttpMethods,
    ServiceName,
    SetRequest,
    SuccessResponse,
    UsersRoutes,
)


@pytest_asyncio.fixture
async def request_client() -> AsyncGenerator[SetRequest, None]:
    """Fixture that provides a SetRequest instance."""
    client = SetRequest()
    yield client


@pytest.mark.asyncio
async def test_get_url_builds_correctly(request_client: SetRequest) -> None:
    url = await request_client._get_url(
        service_name=ServiceName.USERS,
        route_name=UsersRoutes.CREATE_USER,
    )
    assert isinstance(url, str)
    assert url.startswith("http://")
    assert "/users/create" in url


@pytest.mark.asyncio
async def test_validate_http_method_ok() -> None:
    await SetRequest.validate_http_method(
        route_name=UsersRoutes.CREATE_USER,
        route_method=HttpMethods.POST,
    )


@pytest.mark.asyncio
async def test_validate_http_method_invalid() -> None:
    with pytest.raises(ValueError) as exc:
        await SetRequest.validate_http_method(
            route_name=UsersRoutes.CREATE_USER,
            route_method=HttpMethods.GET,
        )
    assert "Invalid HTTP method" in str(exc.value)


@pytest.mark.asyncio
async def test_send_request_success(request_client: SetRequest) -> None:
    fake_response = AsyncMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"msg": "ok"}

    with patch.object(
        request_client, "_ensure_client", return_value=AsyncMock()
    ) as mock_client:
        mock_client.return_value.request.return_value = fake_response

        resp = await request_client.send_request(
            service_name=ServiceName.USERS,
            route_name=UsersRoutes.CREATE_USER,
            route_method=HttpMethods.POST,
            request_data=None,
        )

    assert isinstance(resp, SuccessResponse)
    assert resp.detail == {"msg": "ok"}


@pytest.mark.asyncio
async def test_send_request_4xx_error(request_client: SetRequest) -> None:
    fake_response = AsyncMock()
    fake_response.status_code = 404
    fake_response.json.return_value = {"detail": "Not found"}

    with patch.object(
        request_client, "_ensure_client", return_value=AsyncMock()
    ) as mock_client:
        mock_client.return_value.request.return_value = fake_response

        resp = await request_client.send_request(
            service_name=ServiceName.USERS,
            route_name=UsersRoutes.GET_USER_BY_ID,
            route_method=HttpMethods.GET,
        )

    assert isinstance(resp, ErrorResponse)
    assert resp.error == "Not found"
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_send_request_timeout(request_client: SetRequest) -> None:
    with patch.object(
        request_client, "_ensure_client", return_value=AsyncMock()
    ) as mock_client:
        mock_client.return_value.request.side_effect = TimeoutException(
            "Request timed out"
        )

        with pytest.raises(BaseRequestException) as exc:
            await request_client.send_request(
                service_name=ServiceName.USERS,
                route_name=UsersRoutes.CREATE_USER,
                route_method=HttpMethods.POST,
            )
        assert "Request timed out" in str(exc.value)


@pytest.mark.asyncio
async def test_send_request_json_parse_error(request_client: SetRequest) -> None:
    fake_response = AsyncMock()
    fake_response.status_code = 200
    fake_response.json.side_effect = ValueError("bad json")
    fake_response.text = "not json"

    with patch.object(
        request_client, "_ensure_client", return_value=AsyncMock()
    ) as mock_client:
        mock_client.return_value.request.return_value = fake_response

        with pytest.raises(BaseRequestException) as exc:
            await request_client.send_request(
                service_name=ServiceName.USERS,
                route_name=UsersRoutes.CREATE_USER,
                route_method=HttpMethods.POST,
            )

    assert "Failed to parse response JSON" in str(exc.value)
