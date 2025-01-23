import asyncio

from tools_openverse.common.request import (
    BaseRequestException,
    CreateUserRequest,
    HttpMethods,
    RoutesNamespace,
    ServiceName,
    SetRequest,
)


async def main():
    request_client = SetRequest(timeout=5.0)

    # Создание пользователя
    test_data = CreateUserRequest(
        login="testgted", name="", password="test123", email="test@test.com"
    )

    print(ServiceName.USERS, RoutesNamespace.USERS.CREATE_USER.value)

    try:
        result = await request_client.send_request(
            service_name=ServiceName.USERS,
            route_name=RoutesNamespace.USERS.CREATE_USER,
            route_method=HttpMethods.POST,
            data=test_data,
        )
        print(f"Success: {result}")
    except BaseRequestException as e:
        print(f"Error: {e.detail}")


if __name__ == "__main__":
    asyncio.run(main())
