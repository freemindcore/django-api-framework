from typing import TYPE_CHECKING, Any

from django.http import HttpRequest

from tests.demo_app.domain import EventBiz

if TYPE_CHECKING:
    from ninja_extra.controllers.base import ControllerBase  # pragma: no cover

from easy.services import BaseService


class EventService(BaseService):
    def __init__(self, biz=EventBiz()):
        super().__init__(biz.model)

    @staticmethod
    async def prepare_create_event_data(data):
        """Helper func for unit testing"""
        object_data = data.copy()
        object_data.update(title=f"{object_data['title']}_create")
        return object_data

    async def get_event_objs_demo(self):
        """Demo API for unit testing"""
        return await self.get_objs(maximum=10)

    async def get_identity_demo(self, word):
        """Demo API for unit testing"""
        return dict(says=word)

    def check_permission(
        self, request: HttpRequest, controller: "ControllerBase"
    ) -> bool:
        """
        Overwrite parent check_permission
        """
        user = request.user
        return bool(
            user and user.is_authenticated and user.is_active
        ) and super().check_permission(request, controller)

    def check_object_permission(
        self, request: HttpRequest, controller: "ControllerBase", obj: Any
    ) -> bool:
        """
        Only superuser is granted access
        """
        return bool(request.user.is_superuser) and super().check_object_permission(
            request, controller, obj
        )
