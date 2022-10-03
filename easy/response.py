import json
from typing import Any, Type, Union

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
        data: Union[dict, str] = None,
        errno: int = None,
        message: str = None,
        **kwargs: Any
    ):
        if errno:
            message = message or UNKNOWN_ERROR_MSG
        else:
            message = SUCCESS_MESSAGE
            errno = ERRNO_SUCCESS

        _data: Union[dict, str] = {
            "code": errno,
            "message": message,
            "data": data if data is not None else {},
        }
        _encoder: Type[json.JSONEncoder] = EasyJSONEncoder
        super().__init__(data=_data, encoder=_encoder, **kwargs)

    @property
    def json_data(self) -> Any:
        """
        Get json data
        """
        return json.loads(self.content)

    def update_content(self, data: dict) -> None:
        """
        Update content with new data
        """
        self.content = json.dumps(data)
