from django.contrib import admin
from django.urls import path
from ninja_extra import NinjaExtraAPI

from .controllers import (
    EventControllerAdminAPI,
    EventEasyControllerAPI,
    EventPermissionController,
)

api = NinjaExtraAPI()
api.register_controllers(EventEasyControllerAPI)
api.register_controllers(EventPermissionController)
api.register_controllers(EventControllerAdminAPI)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
