import copy

import pytest
from django.contrib.auth import get_user_model

from easy.controller.base import CrudAPIController
from easy.testing import EasyTestClient
from tests.demo_app.auth import JWTAuthAsync, jwt_auth_async
from tests.demo_app.factories import UserFactory

User = get_user_model()


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory()


@pytest.fixture
def easy_api_client(user) -> EasyTestClient:
    orig_func = copy.deepcopy(JWTAuthAsync.__call__)

    async def mock_func(self, request):
        setattr(request, "user", user)
        return True

    setattr(JWTAuthAsync, "__call__", mock_func)

    def create_client(
        api: CrudAPIController,
        is_staff: bool = False,
        is_superuser: bool = False,
    ):
        setattr(user, "is_staff", is_staff)
        setattr(user, "is_superuser", is_superuser)
        client = EasyTestClient(api, auth=jwt_auth_async)
        return client

    yield create_client
    setattr(JWTAuthAsync, "__call__", orig_func)
