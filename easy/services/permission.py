import logging
from typing import TYPE_CHECKING, Any

from django.http import HttpRequest

if TYPE_CHECKING:
    from ninja_extra.controllers.base import ControllerBase  # pragma: no cover


logger = logging.getLogger(__name__)


class PermissionService(object):
    """Base permission service for extra customization needs"""

    def check_permission(
        self, request: HttpRequest, controller: "ControllerBase"
    ) -> bool:
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return True

    def check_object_permission(
        self, request: HttpRequest, controller: "ControllerBase", obj: Any
    ) -> bool:
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return True
