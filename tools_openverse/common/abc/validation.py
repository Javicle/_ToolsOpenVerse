from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel, field_validator

T = TypeVar("T")


class AbstractValidation(ABC, BaseModel, Generic[T]):
    """Abstract Validation class for users"""

    value: T

    @field_validator("value")
    @classmethod
    @abstractmethod
    def validate(cls, value: T) -> "AbstractValidation[T]":
        pass
