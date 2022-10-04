import logging
from typing import Optional

from ninja_extra import ControllerBase

from easy.controller.meta import CrudAPI, CrudApiMetaclass
from easy.services import BaseService

logger = logging.getLogger(__name__)


class CrudAPIController(ControllerBase, CrudAPI, metaclass=CrudApiMetaclass):
    """For Client facing APIs"""

    def __init__(self, service: Optional["BaseService"] = None):
        super().__init__(service=service)  # type: ignore
