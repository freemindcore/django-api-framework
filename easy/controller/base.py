import logging

from ninja_extra import ControllerBase

from easy.controller.meta import AdminApiMetaclass, CrudAPI, CrudApiMetaclass

logger = logging.getLogger(__name__)


class BaseAdminAPIController(ControllerBase, CrudAPI, metaclass=AdminApiMetaclass):
    """For AdminAPI"""

    def __init__(self, service=None):
        super().__init__(service=service)


class CrudAPIController(ControllerBase, CrudAPI, metaclass=CrudApiMetaclass):
    """For Client facing APIs"""

    def __init__(self, service=None):
        super().__init__(service=service)
