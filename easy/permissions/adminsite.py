from typing import TYPE_CHECKING

from django.http import HttpRequest
from ninja_extra.permissions import IsAdminUser

if TYPE_CHECKING:
    from ninja_extra.controllers.base import ControllerBase  # pragma: no cover


class AdminSitePermission(IsAdminUser):
    """
    Allows delete only to super user, and change to only staff/super users.
    """

    def has_permission(
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
            if request.method in ("GET", "OPTIONS"):
                has_perm = user.has_perm(f"{app}.view{model.__name__}")
            elif request.method in ("PUT",):
                has_perm = user.has_perm(f"{app}.add_{model.__name__}")
            elif request.method in ("PATCH", "POST"):
                has_perm = user.has_perm(f"{app}.change_{model.__name__}")
            elif request.method in ("DELETE",):
                has_perm = user.has_perm(f"{app}.delete_{model.__name__}")
        if user.is_superuser:
            has_perm = True
        return bool(
            user
            and user.is_authenticated
            and user.is_active
            and has_perm
            and super().has_permission(request, controller)
        )

    # async def has_permission(
    #     self, request: HttpRequest, controller: "ControllerBase"
    # ) -> bool:
    #     """
    #     Return `True` if permission is granted, `False` otherwise.
    #     """
    #     user = request.user
    #     has_perm = False
    #     if hasattr(controller, "model"):
    #         model = controller.model
    #         app = model._meta.app_label
    #         has_perm = await sync_to_async(user.has_perm)(
    #             f"{app}.view_{model.__name__}"
    #         )
    #         if request.method in ("PUT",):
    #             has_perm = await sync_to_async(user.has_perm)(
    #                 f"{app}.add_{model.__name__}"
    #             )
    #         if request.method in ("PATCH", "POST"):
    #             has_perm = await sync_to_async(user.has_perm)(
    #                 f"{app}.change_{model.__name__}"
    #             )
    #         if request.method in ("DELETE",):
    #             has_perm = await sync_to_async(user.has_perm)(
    #                 f"{app}.delete_{model.__name__}"
    #             )
    #     if user.is_superuser:
    #         has_perm = True
    #     return bool(user and user.is_authenticated and user.is_active and has_perm)
