from django.contrib import admin
from django.urls import path

from easy import EasyAPI

from .controllers import (
    AutoGenCrudAPIController,
    EasyCrudAPIController,
    PermissionAPIController,
)

api = EasyAPI()
api.register_controllers(EasyCrudAPIController)
api.register_controllers(PermissionAPIController)
api.register_controllers(AutoGenCrudAPIController)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
