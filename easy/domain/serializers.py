import logging
from typing import Any, Dict, List, Tuple

from django.db import models

logger = logging.getLogger(__name__)


class DjangoSerializer(object):
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
            if self.is_one_relationship(field) and self.show_field(obj, field.name):
                out.update(self.serialize_foreign_key(obj, field, referrers + (obj,)))

            elif self.is_many_relationship(field) and self.show_field(obj, field.name):
                out.update(self.serialize_many_relationship(obj, referrers + (obj,)))

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

        if self.get_configuration(obj, "model_recursive", default=False):
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
                    if self.get_configuration(obj, "model_join", default=True):
                        out[field_name] = self.serialize_queryset(v, referrers + (obj,))
                    else:
                        out[field_name] = [o.pk for o in v]
                else:
                    out[field_name] = []
        except Exception as exc:  # pragma: no cover
            logger.error(f"serialize_many_relationship error - {obj}", exc_info=exc)
        return out

    @staticmethod
    def get_configuration(obj: models.Model, _name: str, default: Any = None) -> Any:
        _value = default if default else None
        if hasattr(obj, "__Meta"):
            _value = getattr(obj, "__Meta").get(_name, None)
        return _value

    def get_model_fields_list(self, obj: models.Model) -> Any:
        model_fields = self.get_configuration(obj, "model_fields")
        return model_fields

    def get_model_exclude_list(self, obj: models.Model) -> Any:
        return self.get_configuration(obj, "model_exclude")

    def get_sensitive_list(self, obj: models.Model) -> Any:
        return self.get_configuration(obj, "sensitive_fields")

    def get_final_excluded_list(self, obj: models.Model) -> Any:
        total_excluded_list = []
        sensitive_list: List = ["password", "token"]
        excluded_list = []

        sensitive_fields = self.get_sensitive_list(obj)
        if sensitive_fields:
            sensitive_list.extend(sensitive_fields)
        sensitive_list = list(set(sensitive_list))

        excluded_fields = self.get_model_exclude_list(obj)
        if excluded_fields:
            excluded_list.extend(excluded_fields)
        excluded_list = list(set(excluded_list))

        total_excluded_list.extend(sensitive_list)
        total_excluded_list.extend(excluded_list)
        return list(set(total_excluded_list))

    def show_field(self, obj: models.Model, field_name: str) -> bool:
        model_exclude_list = self.get_model_exclude_list(obj)
        if model_exclude_list:
            if field_name in self.get_final_excluded_list(obj):
                return False
        else:
            if field_name in self.get_final_excluded_list(obj):
                return False
            model_fields_list = self.get_model_fields_list(obj)
            if model_fields_list != "__all__":
                if field_name not in model_fields_list:
                    return False
        return True

    def serialize_value_field(self, obj: models.Model, field: Any) -> Dict[Any, Any]:
        """
        Serializes regular 'jsonable' field (Char, Int, etc.) of Django model instance
        """
        if not self.show_field(obj, field.name):
            return {}
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
