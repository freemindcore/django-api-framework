import logging
from typing import Any

from django.db.models.query import QuerySet
from ninja_extra.shortcuts import get_object_or_none

from easy.response import BaseApiResponse

logger = logging.getLogger(__name__)


class CrudModel(object):
    def __init__(self, model):
        self.model = model

    # Define BASE CRUD
    def _crud_add_obj(self, **payload):
        obj = self.model.objects.create(**payload)
        return obj

    def _crud_del_obj(self, id):
        obj = get_object_or_none(self.model, id=id)
        if obj:
            self.model.objects.filter(id=id).delete()
            return BaseApiResponse({"Detail": "Deleted."})
        else:
            return BaseApiResponse(
                {"Detail": "Not found."}, message="Not found."
            )  # pragma: no cover

    def _crud_update_obj(self, id, payload):
        try:
            obj, created = self.model.objects.update_or_create(id=id, defaults=payload)
        except Exception as e:  # pragma: no cover
            logger.error(f"Crud_update Error - {e}", exc_info=True)
            return BaseApiResponse(message="Failed")
        return BaseApiResponse({"id": obj.id, "created": created})

    def _crud_get_obj(self, id):
        return get_object_or_none(self.model, id=id)

    def _crud_get_objs_all(self, maximum: int = None, **filters) -> QuerySet:
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

    def _crud_filter(self, **kwargs: Any):
        return self.model.objects.filter(**kwargs)

    def _crud_filter_exclude(self, qs: QuerySet = None, **kwargs: Any):
        if qs:
            return qs.exclude(**kwargs)
        else:
            return self.model.objects.all().exclude(**kwargs)


class BaseOrm(CrudModel):
    ...
