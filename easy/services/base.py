import logging
from typing import Type, Union

from django.db import models

from easy.domain import BaseDomain
from easy.services.crud import CrudService
from easy.services.permission import PermissionService

logger = logging.getLogger(__name__)


class BaseService(CrudService, PermissionService):
    def __init__(
        self,
        model: models.Model,
        biz: Union[Type[BaseDomain], None] = None,
    ):
        self.biz = biz
        if self.biz:
            self.model = self.biz.model  # pragma: no cover
        else:
            self.model = model
        super().__init__(model=self.model)
