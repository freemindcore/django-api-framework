from typing import List

from asgiref.sync import sync_to_async
from ninja_extra import api_controller, http_get, paginate

from easy.controller.base import CrudAPIController
from easy.permissions import (
    AdminSitePermission,
    BaseApiPermission,
    IsAdminUser,
    IsAuthenticated,
    IsSuperUser,
)
from easy.response import BaseApiResponse

from .models import Client, Event
from .schema import EventSchema
from .services import EventService


@api_controller("unittest", permissions=[BaseApiPermission])
class AutoGenCrudAPIController(CrudAPIController):
    """
    For unit testings of the following auto generated APIs:
        get/create/patch/delete
    """

    def __init__(self, service: EventService):
        super().__init__(service)

    class Meta:
        model = Event
        model_join = True


@api_controller("unittest", permissions=[BaseApiPermission])
class RecursiveAPIController(CrudAPIController):
    """
    For unit testings of recursive configuration
    """

    def __init__(self, service: EventService):
        super().__init__(service)

    class Meta:
        model = Event
        model_fields = "__all__"
        model_join = True
        model_recursive = True


@api_controller("unittest", permissions=[BaseApiPermission])
class InheritedRecursiveAPIController(AutoGenCrudAPIController):
    """
    For unit testings of inherited recursive configuration
    """

    def __init__(self, service: EventService):
        super().__init__(service)

    class Meta:
        model = Event
        model_fields = "__all__"
        model_join = True
        model_recursive = True


@api_controller("unittest", permissions=[BaseApiPermission])
class AutoGenCrudNoJoinAPIController(CrudAPIController):
    """
    For unit testings of mo model_join and sensitive_fields configuration
    """

    def __init__(self, service: EventService):
        super().__init__(service)

    class Meta:
        model = Event
        model_fields = "__all__"
        model_join = False
        model_recursive = True
        sensitive_fields = ["password", "sensitive_info"]


@api_controller("unittest", permissions=[BaseApiPermission])
class AutoGenCrudSomeFieldsAPIController(CrudAPIController):
    """
    For unit testings of the no-m2m-fields model
    """

    class Meta:
        model = Client
        model_fields = [
            "key",
            "name",
        ]


@api_controller("unittest")
class EasyCrudAPIController(CrudAPIController):
    """
    For unit testings of demo APIs
    """

    def __init__(self, service: EventService):
        super().__init__(service)

    class Meta:
        model = Event
        model_exclude = [
            "category",
        ]

    @http_get("/base_response/")
    async def generate_base_response(self, request):
        return BaseApiResponse({"data": "This is a BaseApiResponse."})

    @http_get("/qs_paginated/", auth=None)
    @paginate
    async def qs_paginated(self, request):
        return await self.service.get_event_objs_demo()

    @http_get("/qs_list/", response=List[EventSchema])
    async def get_objs_list_with_filter_exclude(self, request):
        return await sync_to_async(list)(
            await self.service.filter_exclude_objs(
                title__endswith="qs_list",
            )
        )

    @http_get(
        "/qs/",
    )
    async def list_events(self):
        qs = await sync_to_async(self.service.crud_get_objs_all)(maximum=10)
        await sync_to_async(list)(qs)
        if qs:
            return qs
        return BaseApiResponse()


@api_controller("unittest")
class PermissionAPIController(CrudAPIController):
    """
    For unit testings of permissions class
    """

    def __init__(self, service: EventService):
        super().__init__(service)
        self.service = service

    class Meta:
        model = Event

    @http_get("/must_be_authenticated/", permissions=[IsAuthenticated])
    async def must_be_authenticated(self, word: str):
        return await self.service.get_identity_demo(word)

    @http_get("/must_be_admin_user/", permissions=[IsAdminUser])
    async def must_be_admin_user(self, word: str):
        return await self.service.get_identity_demo(word)

    @http_get("/must_be_super_user/", permissions=[IsSuperUser])
    async def must_be_super_user(self, word: str):
        return await self.service.get_identity_demo(word)

    @http_get("/test_perm_only_super/", permissions=[BaseApiPermission])
    async def test_perm_only_super(self, request):
        event_id = await self.service.add_obj(title="test_event_title")
        # return await self.service.get_obj(id=note.id)
        return await sync_to_async(self.get_object_or_none)(Event, id=event_id)

    @http_get("/test_perm/", permissions=[BaseApiPermission])
    async def test_perm(self, request, word: str):
        return await self.service.get_identity_demo(word)

    @http_get("/test_perm_admin_site/", permissions=[AdminSitePermission])
    async def test_perm_admin_site(self, request, word: str):
        return await self.service.get_identity_demo(word)


@api_controller("unittest", permissions=[AdminSitePermission])
class AdminSitePermissionAPIController(CrudAPIController):
    """
    For unit testings of AdminSite permissions class
    """

    def __init__(self, service: EventService):
        super().__init__(service)
        self.service = service

    class Meta:
        model = Event


@api_controller("unittest", permissions=[AdminSitePermission])
class NoCrudAPIController(CrudAPIController):
    """
    For unit testings of no crud configuration
    """

    def __init__(self, service: EventService):
        super().__init__(service)
        self.service = service

    class Meta:
        model = Event
        generate_crud = False


@api_controller("unittest", permissions=[AdminSitePermission])
class NoCrudInheritedAPIController(AdminSitePermissionAPIController):
    """
    For unit testings of no crud configuration (Inherited Class)
    """

    def __init__(self, service: EventService):
        super().__init__(service)
        self.service = service

    class Meta:
        model = Event
        generate_crud = False
        model_exclude = [
            "start_date",
        ]
