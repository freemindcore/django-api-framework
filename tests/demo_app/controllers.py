from typing import List

from asgiref.sync import sync_to_async
from django.shortcuts import get_object_or_404
from ninja_extra import api_controller, http_get, http_post, paginate

from easy.controller.base import BaseAdminAPIController, CrudAPIController
from easy.permissions import (
    BaseApiPermission,
    IsAdminUser,
    IsAuthenticated,
    IsSuperUser,
)
from tests.demo_app.models import Event
from tests.demo_app.schema import EventSchema, EventSchemaOut
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


@api_controller("unittest")
class EventControllerTest2API(CrudAPIController):
    def __init__(self, service: EventService):
        super().__init__(service)
        self.service = service

    class Meta:
        model = Event
        exclude = [
            "category",
        ]
        recursive = True

    @http_get("/demo", summary="unit test only", auth=None)
    @paginate
    async def demo_api(self, request):
        await self.service.dummy_biz_logics()
        return await self.service.get_objs()


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
class EventControllerAPI(BaseAdminAPIController):
    def __init__(self, service: EventService):
        super().__init__(service)
        self.service = service

    class Meta:
        model = Event
        exclude = [
            "category",
        ]

    @http_get("/crud_get_objs_all", summary="crud_get_objs_all unittest")
    @paginate
    async def get_objs_all_with_filters(self, request, maximum: int = None, **filters):
        await self.service.dummy_biz_logics()
        await self.service.demo_action(data="running /get_objs_all_with_filters")
        return await self.service.get_objs(maximum, **filters)

    @http_get("/crud_filter", summary="crud_filter unittest")
    @paginate
    async def get_objs_with_filters(self, request):
        await self.service.demo_action(data="running /get_objs_with_filters")
        return await self.service.filter_objs(id__gte=1)

    @http_get("/crud_filter_exclude", summary="crud_filter_exclude unittest")
    @paginate
    async def get_objs_with_crud_filter_exclude(self, request):
        await self.service.demo_action(
            data="running /get_objs_with_crud_filter_exclude"
        )
        return await self.service.filter_exclude_objs(id__lt=1)

    @http_get("/crud_filter_exclude_paginated", response=List[EventSchema])
    async def get_objs_with_crud_filter_exclude_paginated(self, request):
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


@api_controller("events")
class EventController:
    @http_post("", url_name="event-create-url-name", response={201: EventSchemaOut})
    def create_event(self, event: EventSchema):
        event = Event.objects.create(**event.dict())
        return 201, event

    @http_get(
        "",
        response=List[EventSchema],
        url_name="event-list",
    )
    def list_events(self):
        return list(Event.objects.all())

    @http_get(
        "/list",
        response=List[EventSchema],
        url_name="event-list-2",
    )
    def list_events_example_2(self):
        return list(Event.objects.all())

    @http_get("/{int:id}", response=EventSchema)
    def get_event(self, id: int):
        event = get_object_or_404(Event, id=id)
        return event
