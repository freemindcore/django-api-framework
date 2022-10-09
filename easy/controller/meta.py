import json
import logging
import uuid
from abc import ABCMeta
from typing import Any, List, Optional, Tuple, Type, Union

from django.db import models
from django.http import HttpRequest
from ninja import ModelSchema
from ninja_extra import ControllerBase, http_delete, http_get, http_patch, http_put
from ninja_extra.pagination import paginate

from easy.domain.orm import CrudModel
from easy.response import BaseApiResponse
from easy.services import BaseService
from easy.utils import copy_func

logger = logging.getLogger(__name__)


class CrudAPI(CrudModel):
    # Never add type note to service, it will cause injection error
    def __init__(self, service=None):  # type: ignore
        if not service:
            self.service = BaseService(model=self.model)
        else:
            self.service = service
        super().__init__(model=self.model)

        # Critical to set Meta
        if hasattr(self, "Meta"):
            self.model.Meta = self.Meta  # type: ignore

    # Define Controller APIs for auto generation
    async def get_obj(self, request: HttpRequest, id: int) -> Any:
        """
        GET /{id}
        Retrieve a single Object
        """
        try:
            qs = await self.service.get_obj(id)
        except Exception as e:  # pragma: no cover
            logger.error(f"Get Error - {e}", exc_info=True)
            return BaseApiResponse(str(e), message="Get Failed", errno=500)
        if qs:
            return qs
        else:
            return BaseApiResponse(message="Not Found", errno=404)

    async def del_obj(self, request: HttpRequest, id: int) -> Any:
        """
        DELETE /{id}
        Delete a single Object
        """
        if await self.service.del_obj(id):
            return BaseApiResponse("Deleted.", errno=204)
        else:
            return BaseApiResponse("Not Found.", errno=404)

    @paginate
    async def get_objs(
        self, request: HttpRequest, maximum: int = None, filters: str = None
    ) -> Any:
        """
        GET /?maximum={int}&filters={filters_dict}
        Retrieve multiple Object (optional: maximum # and filters)
        """
        if filters:
            return await self.service.get_objs(maximum, **json.loads(filters))
        return await self.service.get_objs(maximum)

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


class CrudApiMetaclass(ABCMeta):
    def __new__(mcs, name: str, bases: Tuple[Type[Any], ...], attrs: dict) -> Any:
        # Get configs from Meta
        temp_cls: Type = super(CrudApiMetaclass, mcs).__new__(
            mcs, name, (object,), attrs
        )
        temp_opts: ModelOptions = ModelOptions(getattr(temp_cls, "Meta", None))
        opts_model: Optional[Type[models.Model]] = temp_opts.model
        opts_fields_exclude: Optional[str] = temp_opts.model_exclude
        opts_fields: Optional[str] = temp_opts.model_fields
        opts_recursive: Optional[bool] = temp_opts.model_recursive
        opts_join: Optional[bool] = temp_opts.model_join
        opts_sensitive_fields: Optional[
            Union[str, List[str]]
        ] = temp_opts.sensitive_fields

        base_cls_attrs = {
            "get_obj": http_get("/{id}", summary="Get a single object")(
                copy_func(CrudAPI.get_obj)  # type: ignore
            ),
            "del_obj": http_delete("/{id}", summary="Delete a single object")(
                copy_func(CrudAPI.del_obj)  # type: ignore
            ),
            "get_all": http_get("/", summary="Get multiple objects")(
                copy_func(CrudAPI.get_objs)  # type: ignore
            ),
        }

        if opts_model:

            class DataSchema(ModelSchema):
                class Config:
                    model = opts_model
                    if opts_fields_exclude:
                        model_exclude = opts_fields_exclude
                    else:
                        if opts_fields == "__all__":
                            model_fields = "__all__"
                        else:
                            model_fields = opts_fields if opts_fields else "__all__"

            async def add_obj(  # type: ignore
                self, request: HttpRequest, data: DataSchema
            ) -> Any:
                """
                PUT /
                Create a single Object
                """
                obj_id = await self.service.add_obj(**data.dict())
                if obj_id:
                    return BaseApiResponse({"id": obj_id}, errno=201)
                else:
                    return BaseApiResponse("Add failed", errno=204)  # pragma: no cover

            async def patch_obj(  # type: ignore
                self, request: HttpRequest, id: int, data: DataSchema
            ) -> Any:
                """
                PATCH /{id}
                Update a single object
                """
                if await self.service.patch_obj(id=id, payload=data.dict()):
                    return BaseApiResponse("Updated.")
                else:
                    return BaseApiResponse("Update Failed", errno=400)

            DataSchema.__name__ = (
                f"{opts_model.__name__}__AutoSchema({str(uuid.uuid4())[:4]})"
            )

            setattr(CrudAPI, "add_obj", classmethod(add_obj))
            setattr(CrudAPI, "patch_obj", classmethod(patch_obj))

            base_cls_attrs.update(
                {
                    "patch_obj": http_patch("/{id}", summary="Patch a single object")(
                        copy_func(CrudAPI.patch_obj)  # type: ignore
                    ),
                    "add_obj": http_put("/", summary="Create")(
                        copy_func(CrudAPI.add_obj)  # type: ignore
                    ),
                }
            )

        new_base: Type = type.__new__(
            type, name, (ControllerBase, CrudAPI), base_cls_attrs
        )
        new_cls: Type = super(CrudApiMetaclass, mcs).__new__(
            mcs, name, (new_base,), attrs
        )

        if opts_model:
            setattr(opts_model.Meta, "model_exclude", opts_fields_exclude)
            setattr(opts_model.Meta, "model_fields", opts_fields)
            setattr(opts_model.Meta, "model_recursive", opts_recursive)
            setattr(opts_model.Meta, "model_join", opts_join)
            setattr(opts_model.Meta, "sensitive_fields", opts_sensitive_fields)
            setattr(new_cls, "model", opts_model)
        return new_cls


class ModelOptions:
    def __init__(self, options: object = None):
        """
        Configuration:
            model:              django model
            model_fields:       fields to be included in Schema, default to "__all__"
            model_exclude:      fields to be excluded in Schema
            model_join:         retrieve all m2m/FK fields, default to True
            model_recursive:    recursively retrieve FK models, default to False
        """
        self.model: Optional[Type[models.Model]] = getattr(options, "model", None)
        self.model_fields: Optional[Union[str]] = getattr(options, "model_fields", None)
        self.model_exclude: Optional[Union[str]] = getattr(
            options, "model_exclude", None
        )
        self.model_join: Optional[Union[bool]] = getattr(options, "model_join", True)
        self.model_recursive: Optional[Union[bool]] = getattr(
            options, "model_recursive", False
        )
        self.sensitive_fields: Optional[Union[str, List[str]]] = getattr(
            options, "sensitive_fields", ["token", "password"]
        )
