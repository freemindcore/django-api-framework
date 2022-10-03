from typing import Any, Callable, Dict, Sequence, Type, Union
from unittest.mock import Mock

from ninja.constants import NOT_SET, NOT_SET_TYPE
from ninja.testing.client import NinjaResponse
from ninja_extra import ControllerBase
from ninja_extra.testing.client import NinjaExtraClientBase

from easy.main import EasyAPI


class EasyAPIClientBase(NinjaExtraClientBase):
    def __init__(
        self,
        controller_class: Union[Type[ControllerBase], Type],
        auth: Union[
            Sequence[Callable[..., Any]], Callable[..., Any], NOT_SET_TYPE, None
        ] = NOT_SET,
        api_cls: Union[Type[EasyAPI], Type] = EasyAPI,
    ) -> None:
        api = api_cls(auth=auth)
        assert hasattr(controller_class, "get_api_controller"), "Not a valid object"
        controller_ninja_api_controller = controller_class.get_api_controller()
        assert controller_ninja_api_controller
        controller_ninja_api_controller.set_api_instance(api)
        self._urls_cache = list(controller_ninja_api_controller.urls_paths(""))
        super(NinjaExtraClientBase, self).__init__(api)


class EasyTestClient(EasyAPIClientBase):
    async def _call(self, func: Callable, request: Mock, kwargs: Dict) -> NinjaResponse:
        return NinjaResponse(await func(request, **kwargs))
