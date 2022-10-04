import logging
from typing import Type, Union

from django.db import models
from ninja_extra import ControllerBase, api_controller

from easy.controller.base import CrudAPIController
from easy.permissions import AdminSitePermission

logger = logging.getLogger(__name__)


class AdminClass(object):
    auto_import = True


def create_admin_controller(
    model: models.Model, app_name: str
) -> Union[Type[ControllerBase], Type]:
    """Create AdminAPI class dynamically, permission class set to AdminSitePermission"""
    model_name = model.__name__  # type:ignore
    Meta = type(
        "Meta",
        (object,),
        {"model": model, "fields": "__all__"},
    )

    class_name = f"{model_name}AdminAPIController"

    auto_cls = type.__new__(
        type,
        class_name,
        (
            CrudAPIController,
            AdminClass,
        ),
        {
            "Meta": Meta,
        },
    )

    logger.debug(f"Creating Admin API for f{model.__dict__.items()}")
    return api_controller(
        f"/{app_name}/{model_name.lower()}",
        tags=[f"{model_name} AdminAPI"],
        permissions=[AdminSitePermission],
    )(auto_cls)
