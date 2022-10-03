from typing import List

from asgiref.sync import sync_to_async
from ninja_extra import api_controller, http_get, paginate

from easy.controller.base import BaseAdminAPIController, CrudAPIController
from easy.permissions import (
    BaseApiPermission,
    IsAdminUser,
    IsAuthenticated,
    IsSuperUser,
)
from tests.demo_app.models import Event
from tests.demo_app.schema import EventSchema
from tests.demo_app.services import EventService


@api_controller("unittest")
class EventEasyControllerAPI(CrudAPIController):
    def __init__(self, service: EventService):
        super().__init__(service)

    class Meta:
        model = Event
        exclude = [
            "category",
        ]

    @http_get(
        "/dummy",
    )
    async def dummy_api(self, request):
        await self.service.dummy_biz_logics()
        return {"data": 1}

    @http_get(
        "/list",
    )
    @paginate
    async def list_api(self, request):
        qs = await self.service.filter_objs(id__gte=1)
        return qs

    @http_get("/get_objs", summary="unit test only", auth=None)
    @paginate
    async def demo_api(self, request):
        await self.service.dummy_biz_logics()
        return await self.service.get_objs(maximum=10)


@api_controller("unittest")
class EasyEventPermissionController(CrudAPIController):
    def __init__(self, service: EventService):
        super().__init__(service)
        self.service = service

    class Meta:
        model = Event
        exclude = [
            "category",
        ]

    @http_get("/must_be_authenticated", permissions=[IsAuthenticated])
    async def must_be_authenticated(self, word: str):
        await self.service.demo_action(word)
        return dict(says=word)

    @http_get("/must_be_admin_user", permissions=[IsAdminUser])
    async def must_be_admin_user(self, word: str):
        await self.service.demo_action(word)
        return dict(says=word)

    @http_get("/must_be_super_user", permissions=[IsSuperUser])
    async def must_be_super_user(self, word: str):
        await self.service.demo_action(word)
        return dict(says=word)

    @http_get("/test_perm", permissions=[BaseApiPermission])
    async def test_perm(self, request, word: str):
        await self.service.demo_action(word)
        return dict(says=word)

    @http_get("/test_perm_only_super", permissions=[BaseApiPermission])
    async def test_perm_only_super(self, request):
        event = await self.service.add_obj(title="test_event_title")
        # return await self.service.get_obj(id=note.id)
        return await sync_to_async(self.get_object_or_none)(Event, id=event.id)


@api_controller("events", permissions=[BaseApiPermission])
class EventControllerAdminAPI(BaseAdminAPIController):
    def __init__(self, service: EventService):
        super().__init__(service)
        self.service = service

    class Meta:
        model = Event
        exclude = [
            "category",
        ]

    @http_get("/crud_filter_exclude_paginated", response=List[EventSchema])
    async def get_objs_with_crud_filter_exclude(self, request):
        await self.service.demo_action(data="running /crud_filter_exclude_paginated")
        return await sync_to_async(list)(
            await self.service.filter_exclude_objs(id__lt=1)
        )


@api_controller("unittest", permissions=[IsAuthenticated])
class EventPermissionController:
    def __init__(self, event_service: EventService):
        self.event_service = event_service

    @http_get("/must_be_authenticated", permissions=[IsAuthenticated])
    async def must_be_authenticated(self, word: str):
        await self.event_service.demo_action(word)
        return dict(says=word)

    @http_get("/must_be_admin_user", permissions=[IsAdminUser])
    async def must_be_admin_user(self, word: str):
        await self.event_service.demo_action(word)
        return dict(says=word)
