import logging
from typing import Optional, Type

from django.db import models

from easy.services.crud import CrudService
from easy.services.permission import PermissionService

logger = logging.getLogger(__name__)


class BaseService(CrudService, PermissionService):
    def __init__(self, model: Optional[Type[models.Model]] = None):
        self.model = model
        super().__init__(model=self.model)
