import logging
from typing import Any, Type

from asgiref.sync import sync_to_async
from django.db import models

from easy.domain.orm import DjangoOrmModel

logger = logging.getLogger(__name__)


class CrudService(DjangoOrmModel):
    def __init__(self, model: Type[models.Model]):
        super().__init__(model)
        self.model = model

    async def get_obj(self, id: int) -> Any:
        return await sync_to_async(self.crud_get_obj)(id)

    async def get_objs(self, **filters: Any) -> Any:
        return await sync_to_async(self.crud_get_objs_all)(**filters)

    async def patch_obj(self, id: int, payload: Any) -> Any:
        return await sync_to_async(self.crud_update_obj)(id, payload)

    async def del_obj(self, id: int) -> Any:
        return await sync_to_async(self.crud_del_obj)(id)

    async def add_obj(self, **payload: Any) -> Any:
        return await sync_to_async(self.crud_add_obj)(**payload)

    async def filter_objs(self, **payload: Any) -> Any:
        return await sync_to_async(self.crud_filter)(**payload)  # pragma: no cover

    async def filter_exclude_objs(self, **payload: Any) -> Any:
        return await sync_to_async(self.crud_filter_exclude)(**payload)

    # async def bulk_create_objs(self):
    #     ...
    #
    # async def recover_obj(self):
    #     ...
