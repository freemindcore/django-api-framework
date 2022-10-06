from ninja_extra import status
from ninja_extra.exceptions import APIException


class BaseAPIException(APIException):
    """
    API Exception
    """

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = (
        "There is an unexpected error, please try again later, if the problem "
        "persists, please contact customer support team for further support."
    )


class APIAuthException(BaseAPIException):
    """
    API Auth Exception
    """

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Unauthorized"
