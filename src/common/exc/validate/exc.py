from typing import Callable
from functools import wraps


class BaseValidateException(Exception):
    ...




def http_decorator(func: Callable[BaseValidateException]):
    @wraps(func)
    async def decorator(*args, **kwargs):




