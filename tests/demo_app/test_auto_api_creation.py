from ninja_extra.operation import AsyncOperation

from easy import EasyAPI

api_admin_v1 = EasyAPI()
api_admin_v1.auto_create_admin_controllers()


def test_auto_generate_admin_api():
    assert len(api_admin_v1._routers) == 5  # default + 3 models
    path_names = []
    controllers = []
    for path, rtr in api_admin_v1._routers:
        path_names.append(path)
        controllers.append(str(rtr))
        for path_ops in rtr.path_operations.values():
            for op in path_ops.operations:
                assert isinstance(op, AsyncOperation)
                assert op.api is api_admin_v1

    assert "/demo_app/category" in path_names
    assert "/demo_app/client" in path_names
    assert "/demo_app/event" in path_names
    assert "/demo_app/type" in path_names

    assert "CategoryAdminAPIController" in controllers
    assert "EventAdminAPIController" in controllers
    assert "ClientAdminAPIController" in controllers
    assert "TypeAdminAPIController" in controllers


def test_auto_generation_settings(settings):
    settings.AUTO_ADMIN_EXCLUDE_APPS = ["tests.demo_app"]
    api_admin_v2 = EasyAPI()
    api_admin_v2.auto_create_admin_controllers()
    assert len(api_admin_v2._routers) == 1

    settings.AUTO_ADMIN_ENABLED_ALL_APPS = False
    settings.AUTO_ADMIN_EXCLUDE_APPS = []
    settings.AUTO_ADMIN_INCLUDE_APPS = ["tests.none_existing_app"]
    api_admin_v3 = EasyAPI()
    api_admin_v3.auto_create_admin_controllers()
    assert len(api_admin_v3._routers) == 1
