from typing import TYPE_CHECKING

from django.http import HttpRequest

from .base import BaseApiPermission

if TYPE_CHECKING:
    from ninja_extra.controllers.base import ControllerBase  # pragma: no cover


class IsSuperUser(BaseApiPermission):
    """
    Allows access only to super user.
    """

    def has_permission(
        self, request: HttpRequest, controller: "ControllerBase"
    ) -> bool:
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        user = request.user or request.auth  # type: ignore
        return bool(user and user.is_authenticated and user.is_superuser)  # type: ignore
