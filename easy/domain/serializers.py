import logging
from typing import Any, Dict, List, Tuple

from django.db import models

from easy.controller.meta_conf import ModelMetaConfig

logger = logging.getLogger(__name__)


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
