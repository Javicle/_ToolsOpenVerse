"""
Dependency injection module.
"""

from typing import Annotated

from fastapi import Header

authorization = Annotated[str, Header(..., description="Authorization token")]
