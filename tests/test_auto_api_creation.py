import pytest
from ninja_extra.operation import AsyncOperation

from easy import EasyAPI

api_admin_v1 = EasyAPI()
api_admin_v1.auto_create_admin_controllers()

path_names = []
controllers = []
controller_names = []

for path, rtr in api_admin_v1._routers:
    path_names.append(path)
    controllers.append(rtr)
    controller_names.append(str(rtr))
    for path_ops in rtr.path_operations.values():
        for op in path_ops.operations:
            assert isinstance(op, AsyncOperation)
            assert op.api is api_admin_v1


def test_auto_generate_admin_api():
    assert len(api_admin_v1._routers) == 5  # default + 3 models
    assert "/easy_app/category" in path_names
    assert "/easy_app/client" in path_names
    assert "/easy_app/event" in path_names
    assert "/easy_app/type" in path_names

    assert "CategoryAdminAPIController" in controller_names
    assert "EventAdminAPIController" in controller_names
    assert "ClientAdminAPIController" in controller_names
    assert "TypeAdminAPIController" in controller_names


async def test_auto_apis(transactional_db, user, easy_api_client):
    for controller_class in controllers:
        if str(controller_class).endswith("ClientAdminAPIController"):
            client = easy_api_client(controller_class, api_user=user, has_perm=True)
            response = await client.get("/", data={}, json={}, user=user)
            assert response.status_code == 403

            client = easy_api_client(
                controller_class, api_user=user, has_perm=True, is_staff=True
            )
            response = await client.get("/", data={}, json={}, user=user)
            assert response.status_code == 200
            assert response.json()["data"] == []

            client = easy_api_client(
                controller_class, api_user=user, has_perm=True, is_staff=True
            )
            response = await client.delete("/20000")
            assert response.status_code == 403

            client = easy_api_client(
                controller_class, api_user=user, has_perm=True, is_staff=True
            )
            response = await client.delete("/20000", data={}, json={}, user=user)
            assert response.status_code == 200
            assert response.json()["code"] == 404
        elif str(controller_class).endswith("CategoryAdminAPIController"):
            client = easy_api_client(controller_class, api_user=user, has_perm=True)
            with pytest.raises(Exception):
                await client.get("/", data={}, json={}, user=user)


async def test_auto_generation_settings(settings):
    settings.AUTO_ADMIN_EXCLUDE_APPS = ["tests.easy_app"]
    api_admin_v2 = EasyAPI()
    api_admin_v2.auto_create_admin_controllers()
    assert len(api_admin_v2._routers) == 1

    settings.AUTO_ADMIN_ENABLED_ALL_APPS = False
    settings.AUTO_ADMIN_EXCLUDE_APPS = []
    settings.AUTO_ADMIN_INCLUDE_APPS = ["tests.none_existing_app"]
    api_admin_v3 = EasyAPI()
    api_admin_v3.auto_create_admin_controllers()
    assert len(api_admin_v3._routers) == 1
