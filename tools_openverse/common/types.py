from typing import Union
from uuid import UUID
from .schemas import AbstractValidation
from pydantic import EmailStr

UserId = Union[UUID, AbstractValidation]
UserLogin = Union[str, AbstractValidation]
UserName = Union[str, AbstractValidation]
UserPassword = Union[str, AbstractValidation]
UserEmail = Union[EmailStr, str, AbstractValidation]