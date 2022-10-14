import copy
from typing import Callable, Type, Union

import pytest
from django.contrib.auth import get_user_model
from ninja_extra import ControllerBase, Router

from easy import EasyAPI
from easy.testing import EasyTestClient

from .easy_app.auth import JWTAuthAsync, jwt_auth_async
from .easy_app.factories import UserFactory

User = get_user_model()


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory()


@pytest.fixture
def easy_api_client(user) -> Callable:
    orig_func = copy.deepcopy(JWTAuthAsync.__call__)

    orig_has_perm_fuc = copy.deepcopy(user.has_perm)

    def mock_has_perm_true(*args, **kwargs):
        return True

    def mock_has_perm_false(*args, **kwargs):
        return False

    async def mock_func(self, request):
        setattr(request, "user", user)
        return True

    setattr(JWTAuthAsync, "__call__", mock_func)

    def create_client(
        api: Union[EasyAPI, Router, Type[ControllerBase]],
        is_staff: bool = False,
        is_superuser: bool = False,
        has_perm: bool = False,
    ) -> "EasyTestClient":
        setattr(user, "is_staff", is_staff)
        setattr(user, "is_superuser", is_superuser)
        if is_superuser:
            setattr(user, "is_staff", True)
        if has_perm:
            setattr(user, "has_perm", mock_has_perm_true)
        else:
            setattr(user, "has_perm", mock_has_perm_false)
        client = EasyTestClient(api, auth=jwt_auth_async)
        return client

    yield create_client
    setattr(JWTAuthAsync, "__call__", orig_func)
    setattr(user, "has_perm", orig_has_perm_fuc)
