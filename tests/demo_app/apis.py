from easy.main import EasyAPI
from tests.demo_app.auth import jwt_auth_async
from tests.demo_app.controllers import (
    EventControllerAPI,
    EventEasyControllerAPI,
    EventPermissionController,
)

api_unittest = EasyAPI(auth=jwt_auth_async)
api_unittest.register_controllers(
    EventEasyControllerAPI,
    EventPermissionController,
    EventControllerAPI,
)
