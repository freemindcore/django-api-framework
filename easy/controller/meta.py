import json
import logging
import uuid
from abc import ABCMeta

from ninja import ModelSchema
from ninja_extra import ControllerBase, http_delete, http_get, http_patch, http_put
from ninja_extra.pagination import paginate

from easy.domain.orm import CrudModel
from easy.services import BaseService
from easy.utils import copy_func

logger = logging.getLogger(__name__)


class CrudAPI(CrudModel):
    def __init__(self, service=None):
        if not service:
            self.service = BaseService(model=self.model)  # pragma: no cover
        else:
            self.service = service
        super().__init__(model=self.model)

    # Define Controller APIs for auto generation
    async def get_obj(self, request, id: int):
        """
        GET /{id}
        Retrieve a single Object
        """
        return await self.service.get_obj(id)

    async def del_obj(self, request, id: int):
        """
        DELETE /objects/{id}
        Delete a single Object
        """
        return await self.service.del_obj(id)

    @paginate
    async def get_objs(self, request, maximum: int = None, filters: str = None):
        """
        GET /get_all
        Retrieve multiple Object
        """
        if filters:
            return await self.service.get_objs(maximum, **json.loads(filters))
        return await self.service.get_objs(maximum)

    @paginate
    async def filter_objs(self, request, filters: str = None):
        """
        GET /filter/?filters={filters_dict}
        Filter Objects
        """
        return await self.service.filter_objs(**json.loads(filters))

    @paginate
    async def filter_exclude_objs(self, filters: str = None):
        """
        GET /filter_exclude/?filters={filters_dict}
        Filter exclude Objects
        """
        return await self.service.filter_exclude_objs(**json.loads(filters))

    # async def patch_obj(self, request):
    #     ...
    #
    # async def add_obj(self, request):
    #     ...

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
    def __new__(mcs, name, bases, attrs):
        return mcs.generate_cls(mcs, name, (ControllerBase, CrudAPI), attrs)

    def generate_cls(mcs, name, bases, attrs):
        # Get configs from Meta
        temp_base = type.__new__(type, "object", (), {})
        temp_cls = super(CrudApiMetaclass, mcs).__new__(mcs, name, (temp_base,), attrs)
        temp_opts = ModelOptions(getattr(temp_cls, "Meta", None))
        opts_fields_exclude = temp_opts.exclude
        opts_fields = temp_opts.fields
        opts_model = temp_opts.model
        opts_recursive = temp_opts.recursive

        base_cls_attrs = {
            "get_obj": http_get("/", summary="Get")(copy_func(CrudAPI.get_obj)),
            "del_obj": http_delete("/", summary="Delete")(copy_func(CrudAPI.del_obj)),
            "get_all": http_get("/get_all", summary="Get All")(
                copy_func(CrudAPI.get_objs)
            ),
            "filter_objs": http_get("/filter", summary="Filter")(
                copy_func(CrudAPI.filter_objs)
            ),
            "filter_exclude_objs": http_get(
                "/filter_exclude", summary="Filter exclude"
            )(copy_func(CrudAPI.filter_exclude_objs)),
        }

        if opts_model:

            class DataSchema(ModelSchema):
                class Config:
                    model = opts_model
                    if opts_fields_exclude:
                        model_exclude = opts_fields_exclude
                    else:
                        model_fields = opts_fields if opts_fields else "__all__"
                    recursive = temp_opts.recursive

            async def add_obj(self, request, data: DataSchema):
                """
                PUT /
                Create a single Object
                """
                return await self.service.add_obj(**data.dict())

            async def patch_obj(self, request, id: int, data: DataSchema):
                """
                PATCH /?id={id}
                Update a single field for a Object
                """
                return await self.service.patch_obj(id=id, payload=data.dict())

            DataSchema.__name__ = (
                f"{temp_opts.model.__name__}__AutoSchema({str(uuid.uuid4())[:4]})"
            )

            setattr(CrudAPI, "add_obj", classmethod(add_obj))
            setattr(CrudAPI, "patch_obj", classmethod(patch_obj))
            base_cls_attrs.update(
                {
                    "patch_obj": http_patch("/", summary="Patch/Update")(
                        copy_func(CrudAPI.patch_obj)
                    ),
                    "add_obj": http_put("/", summary="Create")(
                        copy_func(CrudAPI.add_obj)
                    ),
                }
            )

        new_base = type.__new__(type, name, bases, base_cls_attrs)
        new_cls = super(CrudApiMetaclass, mcs).__new__(mcs, name, (new_base,), attrs)

        new_cls.model = opts_model
        new_cls.fields_exclude = opts_fields_exclude
        new_cls.fields = opts_fields
        new_cls.recursive = opts_recursive

        return new_cls


class AdminApiMetaclass(CrudApiMetaclass):
    def __new__(mcs, name, bases, attrs):
        return mcs.generate_cls(mcs, name, (ControllerBase, AdminCrudAPI), attrs)


class ModelOptions:
    def __init__(self, options=None):
        self.model = getattr(options, "model", None)
        self.service = getattr(options, "service", None)
        self.fields = getattr(options, "fields", None)
        self.exclude = getattr(options, "exclude", None)
        self.recursive = getattr(options, "recursive", False)
