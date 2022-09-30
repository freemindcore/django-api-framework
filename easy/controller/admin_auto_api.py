import logging

from ninja_extra import api_controller

from easy.controller.base import BaseAdminAPIController
from easy.permissions import BaseApiPermission

logger = logging.getLogger(__name__)


class AdminClass(object):
    auto_import = True


def create_admin_controller(model, app_name):
    """Create AdminAPI class dynamically"""
    model_name = model.__name__
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
            BaseAdminAPIController,
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
        permissions=[BaseApiPermission],
    )(auto_cls)
