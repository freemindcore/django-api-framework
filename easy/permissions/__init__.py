from ninja_extra.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)

from .base import BaseApiPermission
from .superuser import IsSuperUser

__all__ = [
    "BaseApiPermission",
    "IsSuperUser",
    "AllowAny",
    "IsAuthenticated",
    "IsAdminUser",
    "IsAuthenticatedOrReadOnly",
]
