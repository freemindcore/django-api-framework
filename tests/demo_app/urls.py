from django.contrib import admin
from django.urls import path
from ninja_extra import NinjaExtraAPI

from .controllers import (
    AutoGenCrudAPIController,
    EasyCrudAPIController,
    PermissionAPIController,
)

api = NinjaExtraAPI()
api.register_controllers(EasyCrudAPIController)
api.register_controllers(PermissionAPIController)
api.register_controllers(AutoGenCrudAPIController)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
