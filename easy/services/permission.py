import logging
from typing import TYPE_CHECKING, Any

from asgiref.sync import sync_to_async
from django.http import HttpRequest

if TYPE_CHECKING:
    from ninja_extra.controllers.base import ControllerBase  # pragma: no cover


logger = logging.getLogger(__name__)


class PermissionService(object):
    def check_permission(
        self, request: HttpRequest, controller: "ControllerBase"
    ) -> bool:
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        user = request.user
        has_perm = True
        if request.method == "DELETE":
            has_perm = bool(user.is_superuser)
        if request.method in ("PUT", "PATCH", "POST"):
            has_perm = bool(user.is_staff or user.is_superuser)
        return bool(user and user.is_authenticated and user.is_active and has_perm)

    def check_object_permission(
        self, request: HttpRequest, controller: "ControllerBase", obj: Any
    ) -> bool:
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return True

    def check_permission_v2(
        self, request: HttpRequest, controller: "ControllerBase"
    ) -> bool:
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        user = request.user
        has_perm = True
        if hasattr(controller, "model"):
            model = controller.model
            app = model._meta.app_label
            has_perm = user.has_perm(f"{app}.view_{model.__name__}")
            if request.method in ("PUT",):
                has_perm = user.has_perm(f"{app}.add_{model.__name__}")
            if request.method in ("PATCH", "POST"):
                has_perm = user.has_perm(f"{app}.change_{model.__name__}")
            if request.method in ("DELETE",):
                has_perm = user.has_perm(f"{app}.delete_{model.__name__}")
        if user.is_superuser:
            has_perm = True
        return bool(user and user.is_authenticated and user.is_active and has_perm)

    async def async_check_permission(
        self, request: HttpRequest, controller: "ControllerBase"
    ) -> bool:
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        user = request.user
        has_perm = False
        if hasattr(controller, "model"):
            model = controller.model
            app = model._meta.app_label
            has_perm = await sync_to_async(user.has_perm)(
                f"{app}.view_{model.__name__}"
            )
            if request.method in ("PUT",):
                has_perm = await sync_to_async(user.has_perm)(
                    f"{app}.add_{model.__name__}"
                )
            if request.method in ("PATCH", "POST"):
                has_perm = await sync_to_async(user.has_perm)(
                    f"{app}.change_{model.__name__}"
                )
            if request.method in ("DELETE",):
                has_perm = await sync_to_async(user.has_perm)(
                    f"{app}.delete_{model.__name__}"
                )
        if user.is_superuser:
            has_perm = True
        return bool(user and user.is_authenticated and user.is_active and has_perm)
