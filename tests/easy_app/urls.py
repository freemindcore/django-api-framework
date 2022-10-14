from django.contrib import admin
from django.urls import path

from .apis import api_unittest

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api_unittest.urls),
]
