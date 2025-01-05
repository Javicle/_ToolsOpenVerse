from typing import NewType
from uuid import UUID

UserID = NewType("UserID", UUID)
UserLogin = NewType("UserLogin", str)
UserName = NewType("UserName", str)
UserPassword = NewType("UserPassword", str)
UserEmail = NewType("UserEmail", str)
