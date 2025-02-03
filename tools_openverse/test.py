import asyncio

from tools_openverse.common.request import (
    BaseRequestException,
    HttpMethods,
    LoginModel,
    RoutesNamespace,
    ServiceName,
    SetRequest,
)
from tools_openverse.common.types import ErrorResponse


async def main() -> None:
    request_client = SetRequest(timeout=5.0)

    test_data = LoginModel(
        login="testgtedgfdhgfGfdweDFGD",
        password="tesAt1@23",
    )

    # test_data = CreateUserRequest(
    #     login="testgtedgfdhgfGfdweDFGD",
    #     name="Login",
    #     password="tesAt1@23",
    #     email="testt@dfeFDSst.com",
    # )

    # Получение пользователя
    # test_data = GetUserRequest(
    #     id="8f9402e9-34fa-41ac-9ca2-5e85f95d2e68",
    # )

    print(
        f"Для откладки : {
            ServiceName.USERS} {
                RoutesNamespace.USERS.GET_USER_BY_ID} {
                    HttpMethods.POST} {test_data}"
    )

    try:
        result = await request_client.send_request(
            service_name=ServiceName.USERS,
            route_name=RoutesNamespace.USERS.LOG_IN,
            route_method=HttpMethods.POST,
            request_data=test_data,
        )

        if isinstance(result, ErrorResponse):
            print(f"Error: {result.error}")
        else:
            print(f"Success: {result}")
    except BaseRequestException as e:
        print(f"Error: {e.detail}")


if __name__ == "__main__":
    asyncio.run(main())
