import json
import time

from django.http.response import JsonResponse

from easy.renderer.json import EasyJSONEncoder

ERRNO_SUCCESS = 0
SUCCESS_MESSAGE = "success"
UNKNOWN_ERROR_MSG = "system error"


class BaseApiResponse(JsonResponse):
    """
    Base for all API responses
    """

    def __init__(self, data=None, errno=None, message=None, *args, **kwargs):
        if errno:
            message = message or UNKNOWN_ERROR_MSG
        else:
            message = SUCCESS_MESSAGE
            errno = ERRNO_SUCCESS

        _data = {
            "code": errno,
            "message": message,
            "data": data if data is not None else {},
            "now": int(time.time()),
        }
        super().__init__(data=_data, encoder=EasyJSONEncoder, *args, **kwargs)

    @property
    def json_data(self):
        """
        Get json data
        """
        return json.loads(self.content)

    def update_content(self, data: dict):
        """
        Update content with new data
        """
        self.content = json.dumps(data)
