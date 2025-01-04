from fastapi import HTTPException


class BaseHTTPException(HTTPException):
    def __init__(
        self, status_code: int, detail: str | None = None, headers: dict[str, str] | None = None
    ):
        super().__init__(
            status_code=status_code,
            detail=detail if detail else f"Возникла ошибка :{self.__class__.__name__}",
            headers=headers if headers else None,
        )


class BaseHTTPValidationError(HTTPException):
    def __init__(self, validation_field: str, message: str | None = None):
        super().__init__(
            status_code=400, detail=message if message else f"Ошибка валидации в {validation_field}"
        )
        self.validation_field = validation_field


class HTTPLengthException(BaseHTTPValidationError):
    def __init__(
        self,
        validation_field: str,
        length: int,
        message: str | None = None,
        max_length: int | None = None,
    ):
        detail = (
            f"Длина {validation_field} должна быть не менее {length}. и не более {max_length}"
            if max_length
            else f"Длина {validation_field} должна быть не менее {length}."
        )
        super().__init__(
            validation_field,
            (message if message else detail),
        )
        self.length = length


class HTTPSymbolException(BaseHTTPValidationError):
    def __init__(
        self,
        validation_field: str,
        symbol: str | list[str] | dict[str, str] | set[str],
        must_have: bool,
        message: str | None = None,
    ):
        detail = message
        if not detail:
            detail = (
                f"{validation_field} должен содержать символ {symbol}."
                if must_have
                else f"{validation_field} не должен содержать символ {symbol}."
            )
        super().__init__(validation_field, detail)
        self.symbol = symbol
        self.must_have = must_have


class HTTPNumberException(BaseHTTPValidationError):
    def __init__(
        self,
        validation_field: str,
        number: str | list[str] | set[str],
        message: str | None = None,
    ):
        super().__init__(
            validation_field,
            (
                message
                if message
                else f"{validation_field} должен содержать хотя бы одну цифру {number}"
            ),
        )
        self.number = number
