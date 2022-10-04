from json import dumps as json_dumps
from typing import Any, Callable, Dict, List, Sequence, Type, Union, cast
from unittest.mock import Mock
from urllib.parse import urlencode

from ninja import NinjaAPI, Router
from ninja.constants import NOT_SET, NOT_SET_TYPE
from ninja.testing.client import NinjaClientBase, NinjaResponse
from ninja_extra import ControllerBase

from easy.main import EasyAPI


class EasyAPIClientBase(NinjaClientBase):
    def __init__(
        self,
        router_or_app: Union[EasyAPI, Router, Type[ControllerBase]],
        auth: Union[
            Sequence[Callable[..., Any]], Callable[..., Any], NOT_SET_TYPE, None
        ] = NOT_SET,
        api_cls: Union[Type[EasyAPI], Type] = EasyAPI,
    ) -> None:
        if hasattr(router_or_app, "get_api_controller"):
            api = api_cls(auth=auth)
            controller_ninja_api_controller = router_or_app.get_api_controller()  # type: ignore
            assert controller_ninja_api_controller
            controller_ninja_api_controller.set_api_instance(api)
            self._urls_cache = list(controller_ninja_api_controller.urls_paths(""))
            router_or_app = api
        super().__init__(cast(Union[NinjaAPI, Router], router_or_app))

    def request(
        self,
        method: str,
        path: str,
        data: Dict = {},
        json: Any = None,
        **request_params: Any,
    ) -> "NinjaResponse":
        if json is not None:
            request_params["body"] = json_dumps(json)
        if "query" in request_params and isinstance(request_params["query"], dict):
            query = request_params.pop("query")
            url_encode = urlencode(query)
            path = f"{path}?{url_encode}"
        func, request, kwargs = self._resolve(method, path, data, request_params)
        return self._call(func, request, kwargs)  # type: ignore

    @property
    def urls(self) -> List:
        if not hasattr(self, "_urls_cache"):
            self._urls_cache: List
            if isinstance(self.router_or_app, EasyAPI):
                self._urls_cache = self.router_or_app.urls[0]  # pragma: no cover
            else:
                api = EasyAPI()
                self.router_or_app.set_api_instance(api)  # type: ignore
                self._urls_cache = list(self.router_or_app.urls_paths(""))  # type: ignore
        return self._urls_cache


class EasyTestClient(EasyAPIClientBase):
    async def _call(self, func: Callable, request: Mock, kwargs: Dict) -> NinjaResponse:
        return NinjaResponse(await func(request, **kwargs))
