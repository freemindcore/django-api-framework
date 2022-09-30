from typing import Callable, Dict, Type, Union
from unittest.mock import Mock

from ninja.constants import NOT_SET
from ninja.testing.client import NinjaResponse
from ninja_extra import ControllerBase
from ninja_extra.testing.client import NinjaExtraClientBase

from easy.main import EasyAPI


class EasyAPIClientBase(NinjaExtraClientBase):
    def __init__(
        self,
        controller_class: Union[Type[ControllerBase], Type],
        auth=NOT_SET,
        api_cls=EasyAPI,
    ) -> None:
        api = api_cls(auth=auth)
        assert hasattr(controller_class, "get_api_controller"), "Not a valid object"
        controller_ninja_api_controller = controller_class.get_api_controller()
        assert controller_ninja_api_controller
        controller_ninja_api_controller.set_api_instance(api)
        self._urls_cache = list(controller_ninja_api_controller.urls_paths(""))
        super(NinjaExtraClientBase, self).__init__(api)


class EasyAPITestClient(EasyAPIClientBase):
    def _call(self, func: Callable, request: Mock, kwargs: Dict) -> "NinjaResponse":
        return NinjaResponse(func(request, **kwargs))


class EasyAsyncAPITestClient(EasyAPIClientBase):
    async def _call(self, func: Callable, request: Mock, kwargs: Dict) -> NinjaResponse:
        return NinjaResponse(await func(request, **kwargs))
