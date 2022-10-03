from typing import Optional, Union

from ninja_extra import status
from ninja_extra.exceptions import APIException


class BaseAPIException(APIException):
    """
    API Exception
    """

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "There is an exception, please try again later."

    def __init__(
        self,
        detail: Optional[str] = None,
        code: Optional[Union[int]] = None,
    ) -> None:
        super(BaseAPIException, self).__init__(detail, code)
        if detail:
            self.default_detail = detail
        if code:
            self.status_code = code


class APIAuthException(BaseAPIException):
    """
    API Auth Exception
    """

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Unauthorized"
