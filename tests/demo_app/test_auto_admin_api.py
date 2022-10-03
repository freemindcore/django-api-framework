from ninja_extra.operation import AsyncOperation

from easy.main import EasyAdminAPI

api_admin_v1 = EasyAdminAPI()
api_admin_v1.auto_create_admin_controllers()


def test_auto_generate_admin_api():
    assert len(api_admin_v1._routers) == 4  # default + 3 models
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

    assert "CategoryAdminAPIController" in controllers
    assert "EventAdminAPIController" in controllers
    assert "ClientAdminAPIController" in controllers
