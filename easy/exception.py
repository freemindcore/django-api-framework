from typing import Dict, List, Optional, Union

from ninja_extra import status
from ninja_extra.exceptions import APIException

from easy.response import BaseApiResponse


class BaseAPIException(APIException):
    """
    API Exception
    """

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "There is an exception, please try again later."

    def __init__(
        self,
        detail: Optional[Union[List, Dict, "ErrorDetail", str]] = None,  # NOQA
        code: Optional[Union[str, int]] = None,
    ) -> None:
        super(BaseAPIException, self).__init__(detail, code)
        if detail:
            self.default_detail = detail
        if code:
            self.status_code = code


class APIAuthException(BaseAPIException):
    """
    API权限异常
    """

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Unauthorized"


def http_error_handler(request, exc):
    """
    API异常处理函数
    """
    code = exc.status_code
    msg = str(exc)
    data = {
        "status": code,
        "message": msg,
        "detail": msg,
    }

    return BaseApiResponse(status=code, data=data, errno=code, message=msg)
