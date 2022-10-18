import json
import logging
import re
import uuid
from abc import ABC, ABCMeta
from collections import ChainMap
from typing import Any, List, Match, Optional, Tuple, Type

from django.http import HttpRequest
from ninja import ModelSchema
from ninja_extra import ControllerBase, http_delete, http_get, http_patch, http_put
from ninja_extra.pagination import paginate

from easy.controller.meta_conf import MODEL_FIELDS_ATTR_DEFAULT, ModelOptions
from easy.domain.orm import CrudModel
from easy.response import BaseApiResponse
from easy.services import BaseService
from easy.utils import copy_func

logger = logging.getLogger(__name__)


class CrudAPI(CrudModel, ABC):
    # Never add type note to service, it will cause injection error
    def __init__(self, service=None):  # type: ignore
        # Critical to set __Meta
        self.service = service

        _model_opts: ModelOptions = ModelOptions.get_model_options(self.Meta)
        if self.model and _model_opts:
            ModelOptions.set_model_meta(self.model, _model_opts)

        if not service:
            self.service = BaseService(model=self.model)
        super().__init__(model=self.model)


class CrudApiMetaclass(ABCMeta):
    def __new__(mcs, name: str, bases: Tuple[Type[Any], ...], attrs: dict) -> Any:
        # Get configs from Meta
        attrs_meta = attrs.get("Meta", None)
        model_opts: ModelOptions = ModelOptions.get_model_options(attrs_meta)

        # Get all attrs from parents excluding private ones
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

        # Define Controller APIs for auto generation
        async def get_obj(self, request: HttpRequest, id: int) -> Any:  # type: ignore
            """
            GET /{id}
            Retrieve a single Object
            """
            try:
                qs = await self.service.get_obj(id)
            except Exception as e:  # pragma: no cover
                logger.error(f"Get Error - {e}", exc_info=True)
                return BaseApiResponse(str(e), message="Get Failed", code=500)
            if qs:
                return qs
            else:
                return BaseApiResponse(message="Not Found", code=404)

        async def del_obj(self, request: HttpRequest, id: int) -> Any:  # type: ignore
            """
            DELETE /{id}
            Delete a single Object
            """
            if await self.service.del_obj(id):
                return BaseApiResponse("Deleted.", code=204)
            else:
                return BaseApiResponse("Not Found.", code=404)

        @paginate
        async def get_objs(self, request: HttpRequest, filters: str = None) -> Any:  # type: ignore
            """
            GET /?filters={filters_dict}
            Retrieve multiple Object (optional: django filters)
            """
            if filters:
                return await self.service.get_objs(**json.loads(filters))
            return await self.service.get_objs()

        if model_opts.generate_crud and model_opts.model:
            base_cls_attrs.update(
                {
                    "get_obj": http_get("/{id}", summary="Get a single object")(
                        copy_func(get_obj)  # type: ignore
                    ),
                    "del_obj": http_delete("/{id}", summary="Delete a single object")(
                        copy_func(del_obj)  # type: ignore
                    ),
                    "get_objs": http_get("/", summary="Get multiple objects")(
                        copy_func(get_objs)  # type: ignore
                    ),
                }
            )

            class DataSchema(ModelSchema):
                class Config:
                    model = model_opts.model
                    model_exclude: List = []
                    if model_opts.model_exclude:
                        model_exclude.extend(model_opts.model_exclude)
                        # Remove pk(id) from Create/Update Schema
                        model_exclude.extend([model._meta.pk.name])  # type: ignore
                    else:
                        if model_opts.model_fields == MODEL_FIELDS_ATTR_DEFAULT:
                            # Remove pk(id) from Create/Update Schema
                            model_exclude.extend([model._meta.pk.name])  # type: ignore
                        else:
                            model_fields = (
                                model_opts.model_fields
                                if model_opts.model_fields
                                else MODEL_FIELDS_ATTR_DEFAULT
                            )

            async def add_obj(  # type: ignore
                self, request: HttpRequest, data: DataSchema
            ) -> Any:
                """
                PUT /
                Create a single Object
                """
                obj_id = await self.service.add_obj(**data.dict())
                if obj_id:
                    return BaseApiResponse({"id": obj_id}, code=201, message="Created.")
                else:
                    return BaseApiResponse(
                        code=204, message="Add failed."
                    )  # pragma: no cover

            async def patch_obj(  # type: ignore
                self, request: HttpRequest, id: int, data: DataSchema
            ) -> Any:
                """
                PATCH /{id}
                Update a single object
                """
                if await self.service.patch_obj(id=id, payload=data.dict()):
                    return BaseApiResponse(message="Updated.")
                else:
                    return BaseApiResponse(code=400, message="Updated Failed")

            DataSchema.__name__ = (
                f"{model_opts.model.__name__}__AutoSchema({str(uuid.uuid4())[:4]})"
            )

            base_cls_attrs.update(
                {
                    "patch_obj": http_patch("/{id}", summary="Patch a single object")(
                        copy_func(patch_obj)  # type: ignore
                    ),
                    "add_obj": http_put("/", summary="Create")(
                        copy_func(add_obj)  # type: ignore
                    ),
                }
            )

        new_cls: Type = super().__new__(
            mcs,
            name,
            (
                ControllerBase,
                CrudAPI,
            ),
            base_cls_attrs,
        )

        if model_opts.model:
            ModelOptions.set_model_meta(model_opts.model, model_opts)
            setattr(new_cls, "model", model_opts.model)

        return new_cls
