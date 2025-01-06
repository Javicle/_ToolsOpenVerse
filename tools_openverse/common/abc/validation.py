from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class AbstractValidation(ABC, BaseModel, Generic[T]):
    """Abstract Validation class for users"""

    value: T

    # @field_validator("value")
    @classmethod
    @abstractmethod
    def validate(cls, value: T) -> "AbstractValidation[T]":
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"
