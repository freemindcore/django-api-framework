from easy.main import EasyAPI
from tests.demo_app.auth import jwt_auth_async
from tests.demo_app.controllers import (
    AutoGenCrudAPIController,
    EasyCrudAPIController,
    PermissionAPIController,
)

api_unittest = EasyAPI(auth=jwt_auth_async)
api_unittest.register_controllers(
    EasyCrudAPIController,
    PermissionAPIController,
    AutoGenCrudAPIController,
)
