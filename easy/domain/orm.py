import logging
from typing import Any, Dict, List, Optional, Tuple, Type

from django.db import models, transaction
from ninja_extra.shortcuts import get_object_or_none

from easy.controller.meta_conf import ModelMetaConfig
from easy.domain.meta import CrudModel
from easy.exception import BaseAPIException

logger = logging.getLogger(__name__)


class DjangoOrmModel(CrudModel):
    def __init__(self, model: Type[models.Model]):
        self.model = model
        config = ModelMetaConfig()
        exclude_list = config.get_final_excluded_list(self.model())
        self.m2m_fields_list: List = list(
            _field
            for _field in self.model._meta.get_fields(include_hidden=True)
            if (
                isinstance(_field, models.ManyToManyField)
                and ((_field not in exclude_list) if exclude_list else True)
            )
        )
        super().__init__(self.model)

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


class DjangoSerializer(ModelMetaConfig):
    @staticmethod
    def is_model_instance(data: Any) -> bool:
        return isinstance(data, models.Model)

    @staticmethod
    def is_queryset(data: Any) -> bool:
        return isinstance(data, models.query.QuerySet)

    @staticmethod
    def is_one_relationship(data: Any) -> bool:
        return isinstance(data, models.ForeignKey) or isinstance(
            data, models.OneToOneRel
        )

    @staticmethod
    def is_many_relationship(data: Any) -> bool:
        return (
            isinstance(data, models.ManyToManyRel)
            or isinstance(data, models.ManyToManyField)
            or isinstance(data, models.ManyToOneRel)
        )

    @staticmethod
    def is_paginated(data: Any) -> bool:
        return isinstance(data, dict) and isinstance(
            data.get("items", None), models.query.QuerySet
        )

    def serialize_model_instance(
        self, obj: models.Model, referrers: Any = tuple()
    ) -> Dict[Any, Any]:
        """Serializes Django model instance to dictionary"""
        out = {}
        for field in obj._meta.get_fields():
            if self.show_field(obj, field.name):
                if self.is_one_relationship(field):
                    out.update(
                        self.serialize_foreign_key(obj, field, referrers + (obj,))
                    )

                elif self.is_many_relationship(field):
                    out.update(
                        self.serialize_many_relationship(obj, referrers + (obj,))
                    )

                else:
                    out.update(self.serialize_value_field(obj, field))
        return out

    def serialize_queryset(
        self, data: models.query.QuerySet, referrers: Tuple[Any, ...] = tuple()
    ) -> List[Dict[Any, Any]]:
        """Serializes Django Queryset to dictionary"""
        return [self.serialize_model_instance(obj, referrers) for obj in data]

    def serialize_foreign_key(
        self, obj: models.Model, field: Any, referrers: Any = tuple()
    ) -> Dict[Any, Any]:
        """Serializes foreign key field of Django model instance"""
        try:
            if not hasattr(obj, field.name):
                return {field.name: None}  # pragma: no cover
            related_instance = getattr(obj, field.name)
            if related_instance is None:
                return {field.name: None}
            if related_instance in referrers:
                return {}  # pragma: no cover
            field_value = getattr(related_instance, "pk")
        except Exception as exc:  # pragma: no cover
            logger.error(f"serialize_foreign_key error - {obj}", exc_info=exc)
            return {field.name: None}

        if self.get_model_recursive(obj):
            return {
                field.name: self.serialize_model_instance(related_instance, referrers)
            }
        return {field.name: field_value}

    def serialize_many_relationship(
        self, obj: models.Model, referrers: Any = tuple()
    ) -> Dict[Any, Any]:
        """
        Serializes many relationship (ManyToMany, ManyToOne) of Django model instance
        """
        if not hasattr(obj, "_prefetched_objects_cache"):
            return {}
        out = {}
        try:
            for k, v in obj._prefetched_objects_cache.items():  # type: ignore
                field_name = k if hasattr(obj, k) else k + "_set"
                if v:
                    if self.get_model_join(obj):
                        out[field_name] = self.serialize_queryset(v, referrers + (obj,))
                    else:
                        out[field_name] = [o.pk for o in v]
                else:
                    out[field_name] = []
        except Exception as exc:  # pragma: no cover
            logger.error(f"serialize_many_relationship error - {obj}", exc_info=exc)
        return out

    def serialize_value_field(self, obj: models.Model, field: Any) -> Dict[Any, Any]:
        """
        Serializes regular 'jsonable' field (Char, Int, etc.) of Django model instance
        """
        return {field.name: getattr(obj, field.name)}

    def serialize_data(self, data: Any) -> Any:
        out = data
        # Queryset
        if self.is_queryset(data):
            out = self.serialize_queryset(data)
        # Model
        elif self.is_model_instance(data):
            out = self.serialize_model_instance(data)
        # Add limit_off pagination support
        elif self.is_paginated(data):
            out = self.serialize_queryset(data.get("items"))
        return out


django_serializer = DjangoSerializer()
