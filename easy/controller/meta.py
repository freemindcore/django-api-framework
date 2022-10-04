import json
import logging
import uuid
from abc import ABCMeta
from typing import Any, Optional, Tuple, Type, Union

from django.db import models
from django.http import HttpRequest
from ninja import ModelSchema
from ninja_extra import ControllerBase, http_delete, http_get, http_patch, http_put
from ninja_extra.pagination import paginate

from easy.domain.orm import CrudModel
from easy.services import BaseService
from easy.utils import copy_func

logger = logging.getLogger(__name__)


class CrudAPI(CrudModel):
    def __init__(self, service: "BaseService" = None):
        if not service:
            self.service = BaseService(model=self.model)  # pragma: no cover
        else:
            self.service = service
        super().__init__(model=self.model)

    # Define Controller APIs for auto generation
    async def get_obj(self, request: HttpRequest, id: int) -> Any:
        """
        GET /{id}
        Retrieve a single Object
        """
        return await self.service.get_obj(id)

    async def del_obj(self, request: HttpRequest, id: int) -> Any:
        """
        DELETE /objects/{id}
        Delete a single Object
        """
        return await self.service.del_obj(id)

    @paginate
    async def get_objs(
        self, request: HttpRequest, maximum: int = None, filters: str = None
    ) -> Any:
        """
        GET /get_all
        Retrieve multiple Object
        """
        if filters:
            return await self.service.get_objs(maximum, **json.loads(filters))
        return await self.service.get_objs(maximum)

    @paginate
    async def filter_objs(
        self, request: HttpRequest, filters: Union[str, bytes]
    ) -> Any:
        """
        GET /filter/?filters={filters_dict}
        Filter Objects
        """
        return await self.service.filter_objs(**json.loads(filters))

    @paginate
    async def filter_exclude_objs(self, filters: Union[str, bytes]) -> Any:
        """
        GET /filter_exclude/?filters={filters_dict}
        Filter exclude Objects
        """
        return await self.service.filter_exclude_objs(**json.loads(filters))

    async def patch_obj(self, request: HttpRequest) -> Any:
        ...

    async def add_obj(self, request: HttpRequest) -> Any:
        ...

    # async def bulk_create_objs(self, request):
    #     """
    #     POST /bulk_create
    #     Create multiple Object
    #     """
    #     return await self.service.bulk_create_objs()
    #
    # async def recover_obj(self, request):
    #     """
    #     PATCH /{id}/recover
    #     Recover one Object
    #     """
    #     return await self.service.recover_obj()


class AdminCrudAPI(CrudAPI):
    ...


class CrudApiMetaclass(ABCMeta):
    def __new__(mcs, name: str, bases: Tuple[Type[Any], ...], attrs: dict) -> Any:
        return mcs.generate_cls(mcs, name, (ControllerBase, CrudAPI), attrs)

    @staticmethod
    def generate_cls(
        mcs: Type[Any], name: str, bases: Tuple[Type[Any], ...], attrs: dict
    ) -> Type[Any]:
        # Get configs from Meta
        temp_base: Type = type.__new__(type, "object", (), {})
        temp_cls: Type = super(CrudApiMetaclass, mcs).__new__(
            mcs, name, (temp_base,), attrs
        )
        temp_opts: ModelOptions = ModelOptions(getattr(temp_cls, "Meta", None))
        opts_fields_exclude: Optional[Union[str]] = temp_opts.exclude
        opts_fields: Optional[Union[str]] = temp_opts.fields
        opts_model: Optional[Type[models.Model]] = temp_opts.model
        opts_recursive: Optional[Union[bool]] = temp_opts.recursive

        base_cls_attrs = {
            "get_obj": http_get("/", summary="Get")(
                copy_func(CrudAPI.get_obj)  # type: ignore
            ),
            "del_obj": http_delete("/", summary="Delete")(
                copy_func(CrudAPI.del_obj)  # type: ignore
            ),
            "get_all": http_get("/get_all", summary="Get All")(
                copy_func(CrudAPI.get_objs)  # type: ignore
            ),
            "filter_objs": http_get("/filter", summary="Filter")(
                copy_func(CrudAPI.filter_objs)  # type: ignore
            ),
            "filter_exclude_objs": http_get(
                "/filter_exclude", summary="Filter exclude"
            )(
                copy_func(CrudAPI.filter_exclude_objs)  # type: ignore
            ),
        }

        if opts_model:

            class DataSchema(ModelSchema):
                class Config:
                    model = opts_model
                    if opts_fields_exclude:
                        model_exclude = opts_fields_exclude
                    else:
                        if opts_fields == ["__all__"]:
                            model_fields = "__all__"
                        else:
                            model_fields = opts_fields if opts_fields else "__all__"
                    recursive = temp_opts.recursive

            async def add_obj(  # type: ignore
                self, request: HttpRequest, data: DataSchema
            ) -> Any:
                """
                PUT /
                Create a single Object
                """
                return await self.service.add_obj(**data.dict())

            async def patch_obj(  # type: ignore
                self, request: HttpRequest, id: int, data: DataSchema
            ) -> Any:
                """
                PATCH /?id={id}
                Update a single field for a Object
                """
                return await self.service.patch_obj(id=id, payload=data.dict())

            DataSchema.__name__ = (
                f"{opts_model.__name__}__AutoSchema({str(uuid.uuid4())[:4]})"
            )

            setattr(CrudAPI, "add_obj", classmethod(add_obj))
            setattr(CrudAPI, "patch_obj", classmethod(patch_obj))
            base_cls_attrs.update(
                {
                    "patch_obj": http_patch("/", summary="Patch/Update")(
                        copy_func(CrudAPI.patch_obj)  # type: ignore
                    ),
                    "add_obj": http_put("/", summary="Create")(
                        copy_func(CrudAPI.add_obj)  # type: ignore
                    ),
                }
            )

        new_base: Type = type.__new__(type, name, bases, base_cls_attrs)
        new_cls: Type = super(CrudApiMetaclass, mcs).__new__(
            mcs, name, (new_base,), attrs
        )

        new_cls.model = opts_model
        new_cls.fields_exclude = opts_fields_exclude
        new_cls.fields = opts_fields
        new_cls.recursive = opts_recursive

        return new_cls


class AdminApiMetaclass(CrudApiMetaclass):
    def __new__(mcs, name: str, bases: Union[Type], attrs: dict) -> Any:
        return mcs.generate_cls(mcs, name, (ControllerBase, AdminCrudAPI), attrs)


class ModelOptions:
    def __init__(self, options: object = None):
        self.model: Optional[Type[models.Model]] = getattr(options, "model", None)
        self.service: Optional[Any] = getattr(options, "service", None)
        self.fields: Optional[Union[str]] = getattr(options, "fields", None)
        self.exclude: Optional[Union[str]] = getattr(options, "exclude", None)
        self.recursive: Optional[Union[bool]] = getattr(options, "recursive", False)
