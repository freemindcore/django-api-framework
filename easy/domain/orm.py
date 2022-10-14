import logging
from abc import abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Type

from django.db import models, transaction
from django.db.models.query import QuerySet
from ninja_extra.shortcuts import get_object_or_none

from easy.exception import BaseAPIException

logger = logging.getLogger(__name__)


class CrudModel(object):
    def __init__(self, model: Any):
        self.model = model

    @abstractmethod
    def crud_add_obj(self, **payload: Dict) -> Any:
        raise NotImplementedError

    @abstractmethod
    def crud_del_obj(self, pk: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def crud_update_obj(self, pk: int, payload: Dict) -> bool:
        raise NotImplementedError

    @abstractmethod
    def crud_get_obj(self, pk: int) -> Any:
        raise NotImplementedError

    @abstractmethod
    def crud_get_objs_all(self, maximum: Optional[int] = None, **filters: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def crud_filter(self, **kwargs: Any) -> QuerySet:
        raise NotImplementedError

    @abstractmethod
    def crud_filter_exclude(self, **kwargs: Any) -> QuerySet:
        raise NotImplementedError


class DjangoOrmModel(CrudModel):
    def __init__(self, model: Type[models.Model]):
        self.model = model
        self.m2m_fields_list: List = list(
            _field
            for _field in self.model._meta.get_fields(include_hidden=True)
            if isinstance(_field, models.ManyToManyField)
        )
        super().__init__(model)

    def _separate_payload(self, payload: Dict) -> Tuple[Dict, Dict]:
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

    @staticmethod
    def _crud_set_m2m_obj(obj: models.Model, m2m_fields: Dict) -> None:
        if obj and m2m_fields:
            for _field, _value in m2m_fields.items():
                if _value and isinstance(_value, List):
                    m2m_f = getattr(obj, _field)
                    m2m_f.set(_value)

    # Define BASE CRUD
    @transaction.atomic()
    def crud_add_obj(self, **payload: Dict) -> Any:
        local_f_payload, m2m_f_payload = self._separate_payload(payload)

        try:
            # Create obj with local_fields payload
            obj = self.model.objects.create(**local_f_payload)
            # Save obj with m2m_fields payload
            self._crud_set_m2m_obj(obj, m2m_f_payload)
        except Exception as e:  # pragma: no cover
            raise BaseAPIException(f"Create Error - {e}")
        if obj:
            return obj.id

    def crud_del_obj(self, pk: int) -> bool:
        obj = get_object_or_none(self.model, pk=pk)
        if obj:
            self.model.objects.filter(pk=pk).delete()
            return True
        else:
            return False

    @transaction.atomic()
    def crud_update_obj(self, pk: int, payload: Dict) -> bool:
        local_fields, m2m_fields = self._separate_payload(payload)
        if not self.model.objects.filter(pk=pk).exists():
            return False
        try:
            obj, _ = self.model.objects.update_or_create(pk=pk, defaults=local_fields)
            self._crud_set_m2m_obj(obj, m2m_fields)
        except Exception as e:  # pragma: no cover
            raise BaseAPIException(f"Update Error - {e}")
        return bool(obj)

    def crud_get_obj(self, pk: int) -> Any:
        if self.m2m_fields_list:
            qs = self.model.objects.filter(pk=pk).prefetch_related(
                self.m2m_fields_list[0].name
            )
            for f in self.m2m_fields_list[1:]:
                qs = qs.prefetch_related(f.name)
        else:
            qs = self.model.objects.filter(pk=pk)
        if qs:
            return qs.first()

    def crud_get_objs_all(self, maximum: Optional[int] = None, **filters: Any) -> Any:
        """
        CRUD: get multiple objects, with django orm filters support
        Args:
            maximum: {int}
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

    def crud_filter(self, **kwargs: Any) -> Any:
        return self.model.objects.filter(**kwargs)  # pragma: no cover

    def crud_filter_exclude(self, **kwargs: Any) -> Any:
        return self.model.objects.all().exclude(**kwargs)
