import json
from typing import Any, Dict, List, Union

from django.db.models import QuerySet
from django.http.response import JsonResponse

from easy.renderer.json import EasyJSONEncoder

ERRNO_SUCCESS = 0
SUCCESS_MESSAGE = "success"
UNKNOWN_ERROR_MSG = "system error"


class BaseApiResponse(JsonResponse):
    """
    Base for all API responses
    """

    def __init__(
        self,
        data: Union[Dict, str, bool, List[Any], QuerySet] = None,
        code: int = None,
        message: str = None,
        **kwargs: Any
    ):
        if code:
            message = message or UNKNOWN_ERROR_MSG
        else:
            message = SUCCESS_MESSAGE
            code = ERRNO_SUCCESS

        _data: Union[Dict, str] = {
            "code": code,
            "message": message,
            "data": data if data is not None else {},
        }

        super().__init__(data=_data, encoder=EasyJSONEncoder, **kwargs)

    @property
    def json_data(self) -> Any:
        """
        Get json data
        """
        return json.loads(self.content)

    def update_content(self, data: Dict) -> None:
        """
        Update content with new data
        """
        self.content = json.dumps(data)
