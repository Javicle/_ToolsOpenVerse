from typing import Union
from uuid import UUID
from .schemas import AbstractValidation
from pydantic import EmailStr


BaseUserID = UUID
BaseUserLogin = str
BaseUserName = str
BaseUserPassword = str
BaseUserEmail = EmailStr


UserId = Union[BaseUserID, AbstractValidation[BaseUserID]]
UserLogin = Union[BaseUserLogin, AbstractValidation[BaseUserLogin]]
UserName = Union[BaseUserName, AbstractValidation[BaseUserName]]
UserPassword = Union[BaseUserPassword, AbstractValidation[BaseUserPassword]]
UserEmail = Union[EmailStr, BaseUserEmail, AbstractValidation[BaseUserEmail]]
