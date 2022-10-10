from typing import TYPE_CHECKING, Any

from django.http import HttpRequest
from ninja_extra import permissions

if TYPE_CHECKING:
    from ninja_extra.controllers.base import ControllerBase  # pragma: no cover


class BaseApiPermission(permissions.BasePermission):
    """
    Base permission class that all Permission Class should inherit from.
    This will call service.check_permission for extra check.
    """

    def has_permission(
        self, request: HttpRequest, controller: "ControllerBase"
    ) -> bool:
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        has_perm: bool = True
        if hasattr(controller, "service"):
            has_perm = controller.service.check_permission(request, controller)  # type: ignore
        return has_perm

    def has_object_permission(
        self, request: HttpRequest, controller: "ControllerBase", obj: Any
    ) -> bool:
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        has_perm: bool = True
        if hasattr(controller, "service"):
            has_perm = controller.service.check_object_permission(  # type: ignore
                request, controller, obj
            )
        return has_perm
