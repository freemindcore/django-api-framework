import json
import logging
import re
import uuid
from abc import ABCMeta
from collections import ChainMap
from typing import Any, List, Match, Optional, Tuple, Type, Union

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


class APIControllerBase(ControllerBase):
    """Reserved for customization"""

    ...


class CrudAPI(CrudModel):
    # Never add type note to service, it will cause injection error
    def __init__(self, service=None):  # type: ignore
        # Critical to set __Meta
        self.service = service
        if self.service:
            self.model = self.service.model
        _meta = getattr(self, "Meta", None)
        if self.model and _meta:
            setattr(
                self.model,
                "__Meta",
                {
                    "generate_crud": getattr(_meta, "generate_crud", True),
                    "model_exclude": getattr(_meta, "model_exclude", None),
                    "model_fields": getattr(_meta, "model_fields", "__all__"),
                    "model_recursive": getattr(_meta, "model_recursive", False),
                    "model_join": getattr(_meta, "model_join", True),
                    "sensitive_fields": getattr(
                        _meta, "model_sensitive_fields", ["password", "token"]
                    ),
                },
            )
        if not service:
            self.service = BaseService(model=self.model)
        super().__init__(model=self.model)

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
    async def get_objs(self, request: HttpRequest, filters: str = None) -> Any:
        """
        GET /?maximum={int}&filters={filters_dict}
        Retrieve multiple Object (optional: maximum # and filters)
        """
        if filters:
            return await self.service.get_objs(**json.loads(filters))
        return await self.service.get_objs()


class CrudApiMetaclass(ABCMeta):
    def __new__(mcs, name: str, bases: Tuple[Type[Any], ...], attrs: dict) -> Any:
        # Get configs from Meta
        temp_cls: Type = super().__new__(mcs, name, (object,), attrs)
        temp_opts: ModelOptions = ModelOptions(getattr(temp_cls, "Meta", None))
        opts_model: Optional[Type[models.Model]] = temp_opts.model
        opts_generate_crud: Optional[bool] = temp_opts.generate_crud
        opts_fields_exclude: Optional[str] = temp_opts.model_exclude
        opts_fields: Optional[str] = temp_opts.model_fields
        opts_recursive: Optional[bool] = temp_opts.model_recursive
        opts_join: Optional[bool] = temp_opts.model_join
        opts_sensitive_fields: Optional[
            Union[str, List[str]]
        ] = temp_opts.sensitive_fields

        def is_private_attrs(attr_name: str) -> Optional[Match[str]]:
            return re.match(r"^__[^\d\W]\w*\Z__$", attr_name, re.UNICODE)

        parent_attrs = ChainMap(
            *[attrs]
            + [
                {k: v for (k, v) in vars(base).items() if not (is_private_attrs(k))}
                for base in bases
            ]
        )
        base_cls_attrs: dict = {}
        base_cls_attrs.update(parent_attrs)
        if opts_generate_crud:
            base_cls_attrs.update(
                {
                    "get_obj": http_get("/{id}", summary="Get a single object")(
                        copy_func(CrudAPI.get_obj)  # type: ignore
                    ),
                    "del_obj": http_delete("/{id}", summary="Delete a single object")(
                        copy_func(CrudAPI.del_obj)  # type: ignore
                    ),
                    "get_objs": http_get("/", summary="Get multiple objects")(
                        copy_func(CrudAPI.get_objs)  # type: ignore
                    ),
                }
            )
        if opts_generate_crud and opts_model:

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

            setattr(CrudAPI, "patch_obj", patch_obj)
            setattr(CrudAPI, "add_obj", add_obj)

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

        new_cls: Type = super().__new__(
            mcs,
            name,
            (
                APIControllerBase,
                CrudAPI,
            ),
            base_cls_attrs,
        )

        if opts_model:
            setattr(
                opts_model,
                "__Meta",
                {
                    "generate_crud": opts_generate_crud,
                    "model_exclude": opts_fields_exclude,
                    "model_fields": opts_fields,
                    "model_recursive": opts_recursive,
                    "model_join": opts_join,
                    "sensitive_fields": opts_sensitive_fields,
                },
            )
            setattr(new_cls, "model", opts_model)

        return new_cls


class ModelOptions:
    def __init__(self, options: object = None):
        """
        Configuration reader
        """
        self.model: Optional[Type[models.Model]] = getattr(options, "model", None)
        self.generate_crud: Optional[Union[bool]] = getattr(
            options, "generate_crud", True
        )
        self.model_exclude: Optional[Union[str]] = getattr(
            options, "model_exclude", None
        )
        self.model_fields: Optional[Union[str]] = getattr(
            options, "model_fields", "__all__"
        )
        self.model_join: Optional[Union[bool]] = getattr(options, "model_join", True)
        self.model_recursive: Optional[Union[bool]] = getattr(
            options, "model_recursive", False
        )
        self.sensitive_fields: Optional[Union[str, List[str]]] = getattr(
            options, "sensitive_fields", ["token", "password"]
        )
