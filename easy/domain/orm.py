import logging
from typing import Any, Tuple

from django.db import models
from django.db.models.query import QuerySet
from ninja_extra.shortcuts import get_object_or_none

from easy.domain.serializers import is_many_relationship
from easy.response import BaseApiResponse

logger = logging.getLogger(__name__)


class CrudModel(object):
    def __init__(self, model: models.Model):
        self.model = model

    def __get_fields(self, payload: dict) -> Tuple[dict, dict]:
        m2m_fields = {}
        local_fields = {}
        for field in payload.keys():
            model_field = self.model._meta.get_field(field)
            if is_many_relationship(model_field):
                m2m_fields.update({field: payload[field]})
            else:
                local_fields.update({field: payload[field]})
        return local_fields, m2m_fields

    # Define BASE CRUD
    def _crud_add_obj(self, **payload: dict) -> Any:
        local_fields, m2m_fields = self.__get_fields(payload)
        obj = self.model.objects.create(**local_fields)
        if m2m_fields:
            for field, value in m2m_fields.items():
                if value and isinstance(value, list):
                    m2m_f = getattr(obj, field)
                    m2m_f.set(value)
        return obj

    def _crud_del_obj(self, id: int) -> "BaseApiResponse":
        obj = get_object_or_none(self.model, id=id)
        if obj:
            self.model.objects.filter(id=id).delete()
            return BaseApiResponse({"Detail": "Deleted."})
        else:
            return BaseApiResponse(
                {"Detail": "Not found."}, message="Not found."
            )  # pragma: no cover

    def _crud_update_obj(self, id: int, payload: dict) -> "BaseApiResponse":
        local_fields, m2m_fields = self.__get_fields(payload)
        try:
            obj, created = self.model.objects.update_or_create(
                id=id, defaults=local_fields
            )
        except Exception as e:  # pragma: no cover
            logger.error(f"Crud_update Error - {e}", exc_info=True)
            return BaseApiResponse(message="Failed")
        if m2m_fields:
            for field, value in m2m_fields.items():
                if value:
                    m2m_f = getattr(obj, field)
                    m2m_f.set(value)
        return BaseApiResponse({"id": obj.id, "created": created})

    def _crud_get_obj(self, id: int) -> Any:
        return get_object_or_none(self.model, id=id)

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
        return qs

    def _crud_filter(self, **kwargs: Any) -> QuerySet:
        return self.model.objects.filter(**kwargs)

    def _crud_filter_exclude(self, **kwargs: Any) -> QuerySet:
        return self.model.objects.all().exclude(**kwargs)


class BaseOrm(CrudModel):
    ...
