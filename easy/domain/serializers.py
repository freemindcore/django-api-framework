import logging
from typing import Any, Dict, List, Tuple

from django.db import models

logger = logging.getLogger(__name__)


def is_model_instance(data: Any) -> bool:
    return isinstance(data, models.Model)


def is_queryset(data: Any) -> bool:
    return isinstance(data, models.query.QuerySet)


def is_one_relationship(data: Any) -> bool:
    return isinstance(data, models.ForeignKey) or isinstance(data, models.OneToOneRel)


def is_many_relationship(data: Any) -> bool:
    return (
        isinstance(data, models.ManyToManyRel)
        or isinstance(data, models.ManyToManyField)
        or isinstance(data, models.ManyToOneRel)
    )


def is_paginated(data: Any) -> bool:
    return isinstance(data, dict) and isinstance(
        data.get("items", None), models.query.QuerySet
    )


def serialize_model_instance(
    obj: models.Model, referrers: Any = tuple()
) -> Dict[Any, Any]:
    """Serializes Django model instance to dictionary"""
    out = {}
    for field in obj._meta.get_fields():
        if is_one_relationship(field):
            out.update(serialize_foreign_key(obj, field, referrers + (obj,)))

        elif is_many_relationship(field):
            out.update(serialize_many_relationship(obj, referrers + (obj,)))

        else:
            out.update(serialize_value_field(obj, field))
    return out


def serialize_queryset(
    data: models.query.QuerySet, referrers: Tuple[Any, ...] = tuple()
) -> List[Dict[Any, Any]]:
    """Serializes Django Queryset to dictionary"""
    return [serialize_model_instance(obj, referrers) for obj in data]


def serialize_foreign_key(
    obj: models.Model, field: Any, referrers: Any = tuple()
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
    if hasattr(obj, "Meta") and getattr(obj.Meta, "model_recursive", False):
        return {field.name: serialize_model_instance(related_instance, referrers)}
    return {field.name: field_value}


def serialize_many_relationship(
    obj: models.Model, referrers: Any = tuple()
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
                if hasattr(obj, "Meta") and getattr(obj.Meta, "model_join", True):
                    out[field_name] = serialize_queryset(v, referrers + (obj,))
                else:
                    out[field_name] = [o.pk for o in v]
            else:
                out[field_name] = []
    except Exception as exc:  # pragma: no cover
        logger.error(f"serialize_many_relationship error - {obj}", exc_info=exc)
    return out


def serialize_value_field(obj: models.Model, field: Any) -> Dict[Any, Any]:
    """Serializes regular 'jsonable' field (Char, Int, etc.) of Django model instance"""
    sensitive_list: List = [
        "password",
    ]
    if hasattr(obj, "Meta"):
        sensitive_fields = getattr(obj.Meta, "sensitive_fields", None)
        if sensitive_fields:
            sensitive_list.extend(sensitive_fields)
        sensitive_list = list(set(sensitive_list))
    if field.name in sensitive_list:
        return {}
    return {field.name: getattr(obj, field.name)}


def serialize_django_native_data(data: Any) -> Any:
    out = data
    # Queryset
    if is_queryset(data):
        out = serialize_queryset(data)
    # Model
    elif is_model_instance(data):
        out = serialize_model_instance(data)
    # Add limit_off pagination support
    elif is_paginated(data):
        out = serialize_queryset(data.get("items"))
    return out
