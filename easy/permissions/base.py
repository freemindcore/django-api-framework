from typing import TYPE_CHECKING, Any

from django.http import HttpRequest
from ninja_extra import permissions

if TYPE_CHECKING:
    from ninja_extra.controllers.base import ControllerBase  # pragma: no cover


class BaseApiPermission(permissions.BasePermission):
    """
    Base permission class, only active user will have access
    """

    def has_permission(
        self, request: HttpRequest, controller: "ControllerBase"
    ) -> bool:
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        base_check = True
        if hasattr(controller, "service"):
            base_check = controller.service.check_permission(request, controller)
        return base_check

    def has_object_permission(
        self, request: HttpRequest, controller: "ControllerBase", obj: Any
    ) -> bool:
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        base_check = True
        if hasattr(controller, "service"):
            base_check = controller.service.check_object_permission(
                request, controller, obj
            )
        return base_check
