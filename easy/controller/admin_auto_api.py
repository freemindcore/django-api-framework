import logging
from typing import Optional, Type, Union

from django.db import models
from ninja_extra import ControllerBase, api_controller
from ninja_extra.permissions import BasePermission

from easy.controller.base import CrudAPIController
from easy.permissions import AdminSitePermission, BaseApiPermission

logger = logging.getLogger(__name__)


def create_api_controller(
    model: models.Model,
    app_name: str,
    permission_class: Type[BasePermission] = BaseApiPermission,
    controller_name_prefix: Optional[str] = None,
) -> Union[Type[ControllerBase], Type]:
    """Create APIController class dynamically, with specified permission class"""
    model_name = model.__name__  # type:ignore
    Meta = type(
        "Meta",
        (object,),
        {
            "model": model,
            "model_fields": "__all__",
            "model_recursive": False,
            "model_join": True,
            "sensitive_fields": ["password"],
        },
    )

    class_name = f"{model_name}{controller_name_prefix}APIController"

    auto_cls = type.__new__(
        type,
        class_name,
        (CrudAPIController,),
        {
            "Meta": Meta,
        },
    )

    return api_controller(
        f"/{app_name}/{model_name.lower()}",
        tags=[f"{model_name} {controller_name_prefix}API"],
        permissions=[permission_class],
    )(auto_cls)


def create_admin_controller(
    model: models.Model, app_name: str
) -> Union[Type[ControllerBase], Type]:
    """Create AdminAPI class dynamically, permission class set to AdminSitePermission"""
    return create_api_controller(
        model=model,
        app_name=app_name,
        permission_class=AdminSitePermission,
        controller_name_prefix="Admin",
    )
