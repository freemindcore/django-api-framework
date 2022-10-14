import logging
from importlib import import_module
from typing import Any, Callable, Optional, Sequence, Union

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils.module_loading import module_has_submodule
from ninja.constants import NOT_SET, NOT_SET_TYPE
from ninja.parser import Parser
from ninja.renderers import BaseRenderer
from ninja.types import TCallable
from ninja_extra import NinjaExtraAPI

from easy.controller.auto_api import create_admin_controller
from easy.domain.serializers import django_serializer
from easy.renderer.json import EasyJSONRenderer
from easy.response import BaseApiResponse

logger = logging.getLogger(__name__)


class EasyAPI(NinjaExtraAPI):
    """
    EasyAPI, extensions:
    -Add 2 init params
        Easy_extra: bool = True,
            Can serialize queryset or model, and support pagination
        Easy_output: bool = True,
            If True, will be encapsulated in BaseAPIResponse
    -renderer, default to EasyJSONRenderer
    -Auto generate AdminAPIs, it will read the following settings:
        AUTO_ADMIN_ENABLED_ALL_APPS
        AUTO_ADMIN_EXCLUDE_APPS
        AUTO_ADMIN_INCLUDE_APPS
    """

    def __init__(
        self,
        *,
        title: str = "Easy API",
        version: str = "1.0.0",
        description: str = "",
        openapi_url: Optional[str] = "/openapi.json",
        docs_url: Optional[str] = "/docs",
        docs_decorator: Optional[Callable[[TCallable], TCallable]] = None,
        urls_namespace: Optional[str] = None,
        csrf: bool = False,
        auth: Union[
            Sequence[Callable[..., Any]], Callable[..., Any], NOT_SET_TYPE, None
        ] = NOT_SET,
        renderer: Optional[BaseRenderer] = EasyJSONRenderer(),
        parser: Optional[Parser] = None,
        app_name: str = "ninja",
        easy_extra: bool = True,
        easy_output: bool = True,
    ) -> None:
        super(NinjaExtraAPI, self).__init__(
            title=title,
            version=version,
            description=description,
            openapi_url=openapi_url,
            docs_url=docs_url,
            docs_decorator=docs_decorator,
            urls_namespace=urls_namespace,
            csrf=csrf,
            auth=auth,
            renderer=renderer,
            parser=parser,
        )
        self.docs_decorator = docs_decorator
        self.app_name = app_name
        self.easy_extra = easy_extra
        self.easy_output = easy_output

    def auto_create_admin_controllers(self, version: str = None) -> None:
        for app_module in self.get_installed_apps():
            # If not all
            if not settings.AUTO_ADMIN_ENABLED_ALL_APPS:  # type:ignore
                # Only generate for this included apps
                if settings.AUTO_ADMIN_INCLUDE_APPS is not None:  # type:ignore
                    if (
                        app_module.name
                        not in settings.AUTO_ADMIN_INCLUDE_APPS  # type:ignore
                    ):
                        continue

            # Exclude list
            if app_module.name in settings.AUTO_ADMIN_EXCLUDE_APPS:  # type:ignore
                continue

            try:
                app_module_ = import_module(app_module.name)
                final = []
                if module_has_submodule(app_module_, "models"):
                    # Auto generate AdminAPI
                    for model in app_module.get_models():
                        final.append(
                            create_admin_controller(
                                model, app_module.name.split(".")[1]
                            )
                        )
                self.register_controllers(*final)
            except ImportError as ex:  # pragma: no cover
                raise ex

    @staticmethod
    def get_installed_apps() -> list:
        from django.apps import apps

        return [
            v
            for k, v in apps.app_configs.items()
            if not v.name.startswith("django.") and (not v.name == "easy.api")
        ]

    def create_response(
        self,
        request: HttpRequest,
        data: Any,
        *,
        status: int = None,
        temporal_response: HttpResponse = None,
    ) -> HttpResponse:
        if self.easy_extra:
            try:
                data = django_serializer.serialize_data(data)
            except Exception as e:  # pragma: no cover
                logger.error(f"Creat Response Error - {e}", exc_info=True)
                return BaseApiResponse(str(e), code=500)

        if self.easy_output:
            if temporal_response:
                status = temporal_response.status_code
            assert status

            _temp = BaseApiResponse(
                data, status=status, content_type=self.get_content_type()
            )

            if temporal_response:
                response = temporal_response
                response.content = _temp.content
            else:
                response = _temp

        else:
            response = super().create_response(
                request,
                data,
                status=status,
                temporal_response=temporal_response,
            )
        return response

    def create_temporal_response(self, request: HttpRequest) -> HttpResponse:
        if self.easy_output:
            return BaseApiResponse("", content_type=self.get_content_type())
        else:
            return super().create_temporal_response(request)
