import logging
from typing import Optional, Type, Union

from django.db import models
from ninja_extra import ControllerBase, api_controller
from ninja_extra.permissions import BasePermission

from easy.controller.base import CrudAPIController
from easy.controller.meta_conf import (
    GENERATE_CRUD_ATTR,
    MODEL_EXCLUDE_ATTR,
    MODEL_FIELDS_ATTR,
    MODEL_JOIN_ATTR,
    MODEL_RECURSIVE_ATTR,
    SENSITIVE_FIELDS_ATTR,
    ModelOptions,
)
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

    model_opts: ModelOptions = ModelOptions.get_model_options(
        getattr(model, "ApiMeta", None)
    )

    Meta = type(
        "Meta",
        (object,),
        {
            "model": model,
            GENERATE_CRUD_ATTR: model_opts.generate_crud,
            MODEL_EXCLUDE_ATTR: model_opts.model_exclude,
            MODEL_FIELDS_ATTR: model_opts.model_fields,
            MODEL_RECURSIVE_ATTR: model_opts.model_recursive,
            MODEL_JOIN_ATTR: model_opts.model_join,
            SENSITIVE_FIELDS_ATTR: model_opts.model_fields,
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
