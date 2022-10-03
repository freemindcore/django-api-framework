import json
from typing import Any, Type

from django.db.models.fields.files import FieldFile, ImageFieldFile
from ninja.renderers import JSONRenderer
from ninja.responses import NinjaJSONEncoder


class EasyJSONEncoder(NinjaJSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, ImageFieldFile) or isinstance(o, FieldFile):
            try:
                return o.path
            except NotImplementedError:
                return o.url or o.name  # pragma: no cover
            except ValueError:
                return ""

        return super().default(o)


class EasyJSONRenderer(JSONRenderer):
    encoder_class: Type[json.JSONEncoder] = EasyJSONEncoder
