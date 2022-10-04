import logging
from typing import Type

from django.db import models

from easy.services.crud import CrudService
from easy.services.permission import PermissionService

logger = logging.getLogger(__name__)


class BaseService(CrudService, PermissionService):
    def __init__(
        self,
        model: Type[models.Model],
    ):
        self.model = model
        super().__init__(model=self.model)
