import logging
from typing import Any, Dict, List, Tuple, Type

from django.db import models
from django.db.models.query import QuerySet
from ninja_extra.shortcuts import get_object_or_none

from easy.response import BaseApiResponse

logger = logging.getLogger(__name__)


class CrudModel(object):
    def __init__(self, model: Type[models.Model]):
        self.model = model
        self.m2m_fields_list: List = list(
            _field
            for _field in self.model._meta.get_fields(include_hidden=True)
            if isinstance(_field, models.ManyToManyField)
        )

    def __separate_payload(self, payload: Dict) -> Tuple[Dict, Dict]:
        m2m_fields = {}
        local_fields = {}
        for _field in payload.keys():
            model_field = self.model._meta.get_field(_field)
            if model_field in self.m2m_fields_list:
                m2m_fields.update({_field: payload[_field]})
            else:
                # Handling FK fields ( append _id in the end)
                if self.model._meta.get_field(_field).is_relation:
                    if not f"{_field}".endswith("_id"):
                        local_fields.update({f"{_field}_id": payload[_field]})
                else:
                    local_fields.update({_field: payload[_field]})
        return local_fields, m2m_fields

    # Define BASE CRUD
    def _crud_add_obj(self, **payload: Dict) -> Any:
        local_f_payload, m2m_f_payload = self.__separate_payload(payload)
        # Create obj with local_fields payload
        try:
            obj = self.model.objects.create(**local_f_payload)
        except Exception as e:  # pragma: no cover
            logger.error(f"Crud_add Error - {e}", exc_info=True)
            return BaseApiResponse(str(e), message="Add failed", errno=500)
        # Save obj with m2m_fields payload
        if m2m_f_payload:
            for _field, _value in m2m_f_payload.items():
                if _value and isinstance(_value, List):
                    m2m_f = getattr(obj, _field)
                    m2m_f.set(_value)
        return BaseApiResponse({"id": obj.pk}, errno=201)

    def _crud_del_obj(self, pk: int) -> "BaseApiResponse":
        obj = get_object_or_none(self.model, pk=pk)
        if obj:
            self.model.objects.filter(pk=pk).delete()
            return BaseApiResponse("Deleted.", errno=204)
        else:
            return BaseApiResponse("Not Found.", errno=404)

    def _crud_update_obj(self, pk: int, payload: Dict) -> "BaseApiResponse":
        local_fields, m2m_fields = self.__separate_payload(payload)
        if not self.model.objects.filter(pk=pk).exists():
            return BaseApiResponse("Not Found.", errno=404)
        try:
            obj, _ = self.model.objects.update_or_create(pk=pk, defaults=local_fields)
        except Exception as e:  # pragma: no cover
            logger.error(f"Crud_update Error - {e}", exc_info=True)
            return BaseApiResponse(str(e), message="Update Failed", errno=500)
        if obj and m2m_fields:
            for _field, _value in m2m_fields.items():
                if _value:
                    m2m_f = getattr(obj, _field)
                    try:
                        m2m_f.set(_value)
                    except Exception as e:  # pragma: no cover
                        logger.error(f"Crud_update Error - {e}", exc_info=True)
                        return BaseApiResponse(
                            str(e), message="Update Failed", errno=500
                        )
        return BaseApiResponse({"pk": pk}, message="Updated.")

    def _crud_get_obj(self, pk: int) -> Any:
        try:
            if self.m2m_fields_list:
                qs = self.model.objects.filter(pk=pk).prefetch_related(
                    self.m2m_fields_list[0].name
                )
                for f in self.m2m_fields_list[1:]:
                    qs = qs.prefetch_related(f.name)
            else:
                qs = self.model.objects.filter(pk=pk)
        except Exception as e:  # pragma: no cover
            logger.error(f"Get Error - {e}", exc_info=True)
            return BaseApiResponse(str(e), message="Get Failed", errno=500)
        if qs:
            return qs.first()
        else:
            return BaseApiResponse(message="Not Found", errno=404)

    def _crud_get_objs_all(self, maximum: int = None, **filters: Any) -> Any:
        """
        CRUD: get maximum amount of records, with filters support
        Args:
            maximum:
            filters: {"field_name__lte", 1}

        Returns: qs

        """
        qs = None
        if filters:
            try:
                qs = self.model.objects.filter(**filters)
            except Exception as e:  # pragma: no cover
                logger.error(e)
        elif maximum:
            qs = self.model.objects.all()[:maximum]
        else:
            qs = self.model.objects.all()
        # If there are 2m2_fields
        if self.m2m_fields_list and qs:
            qs = qs.prefetch_related(self.m2m_fields_list[0].name)
            for f in self.m2m_fields_list[1:]:
                qs = qs.prefetch_related(f.name)
        return qs

    def _crud_filter(self, **kwargs: Any) -> QuerySet:
        return self.model.objects.filter(**kwargs)

    def _crud_filter_exclude(self, **kwargs: Any) -> QuerySet:
        return self.model.objects.all().exclude(**kwargs)


class BaseOrm(CrudModel):
    ...
