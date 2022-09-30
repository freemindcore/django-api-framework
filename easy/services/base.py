import logging

from easy.services.crud import CrudService
from easy.services.permission import PermissionService

logger = logging.getLogger(__name__)


class BaseService(CrudService, PermissionService):
    def __init__(self, biz=None, model=None):
        self.biz = biz
        if self.biz:
            self.model = self.biz.model
        else:
            self.model = model
        super().__init__(model=self.model)
