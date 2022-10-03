from django.contrib import admin
from django.urls import path
from ninja_extra import NinjaExtraAPI

from .controllers import (
    EasyAdminAPIController,
    EasyCrudAPIController,
    EasyCrudBasePermissionAPIController,
)

api = NinjaExtraAPI()
api.register_controllers(EasyCrudAPIController)
api.register_controllers(EasyCrudBasePermissionAPIController)
api.register_controllers(EasyAdminAPIController)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
