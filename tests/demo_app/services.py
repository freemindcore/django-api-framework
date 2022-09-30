from typing import TYPE_CHECKING, Any

from django.http import HttpRequest

from tests.demo_app.models import Event

if TYPE_CHECKING:
    from ninja_extra.controllers.base import ControllerBase  # pragma: no cover

from easy.services import BaseService


class EventService(BaseService):
    def __init__(self, model=Event):
        super(EventService, self).__init__(model=model)

    @staticmethod
    async def prepare_create_event_data(data):
        object_data = data.copy()
        object_data.update(title=f"{object_data['title']}_create")
        return object_data

    async def dummy_biz_logics(self):
        print("DEMO DUMMY BIZ LOGICS")
        return {}

    async def demo_action(self, data):
        print(f"DEMO ACTION HERE - {data}")
        ...

    def check_permission(
        self, request: HttpRequest, controller: "ControllerBase"
    ) -> bool:
        """
        Overwrite parent check_permission
        """
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.is_active
            and (user.is_staff or user.is_superuser)
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
