from django.test import RequestFactory
from django.utils.translation import gettext_lazy as _
from ninja_extra import exceptions

from easy import EasyAPI, testing
from easy.exception import APIAuthException, BaseAPIException

api = EasyAPI(urls_namespace="exception")


@api.get("/list_exception")
async def list_exception(request):
    raise BaseAPIException(
        [
            "some error 1",
            "some error 2",
        ]
    )


@api.get("/list_exception_full_detail")
async def list_exception_full(request):
    exception = BaseAPIException(
        [
            "some error 1",
            "some error 2",
        ]
    )
    return exception.get_full_details()


@api.get("/dict_exception")
async def dict_exception(request):
    raise BaseAPIException(dict(error="error 1"))


@api.get("/dict_exception_full_detail")
async def dict_exception_full_detail(request):
    exception = BaseAPIException(dict(error="error 1"))
    return exception.get_full_details()


@api.get("/dict_exception_code_detail")
async def dict_exception_code_detail(request):
    exception = BaseAPIException(dict(error="error 1"))
    return exception.get_codes()


@api.get("/list_exception_code_detail")
async def list_exception_code_detail(request):
    exception = BaseAPIException(["some error"])
    return exception.get_codes()


client = testing.EasyTestClient(api)


class TestException:
    async def test_get_error_details(self):
        example = "string"
        lazy_example = _(example)

        assert exceptions._get_error_details(lazy_example) == example

        assert isinstance(
            exceptions._get_error_details(lazy_example), exceptions.ErrorDetail
        )

        assert (
            exceptions._get_error_details({"nested": lazy_example})["nested"] == example
        )

        assert isinstance(
            exceptions._get_error_details({"nested": lazy_example})["nested"],
            exceptions.ErrorDetail,
        )

        assert exceptions._get_error_details([[lazy_example]])[0][0] == example

        assert isinstance(
            exceptions._get_error_details([[lazy_example]])[0][0],
            exceptions.ErrorDetail,
        )


class TestErrorDetail:
    async def test_eq(self):
        assert exceptions.ErrorDetail("msg") == exceptions.ErrorDetail("msg")
        assert exceptions.ErrorDetail("msg", "code") == exceptions.ErrorDetail(
            "msg", code="code"
        )

        assert exceptions.ErrorDetail("msg") == "msg"
        assert exceptions.ErrorDetail("msg", "code") == "msg"

    async def test_ne(self):
        assert exceptions.ErrorDetail("msg1") != exceptions.ErrorDetail("msg2")
        assert exceptions.ErrorDetail("msg") != exceptions.ErrorDetail(
            "msg", code="invalid"
        )

        assert exceptions.ErrorDetail("msg1") != "msg2"
        assert exceptions.ErrorDetail("msg1", "code") != "msg2"

    async def test_repr(self):
        assert repr(
            exceptions.ErrorDetail("msg1")
        ) == "ErrorDetail(string={!r}, code=None)".format("msg1")
        assert repr(
            exceptions.ErrorDetail("msg1", "code")
        ) == "ErrorDetail(string={!r}, code={!r})".format("msg1", "code")

    async def test_str(self):
        assert str(exceptions.ErrorDetail("msg1")) == "msg1"
        assert str(exceptions.ErrorDetail("msg1", "code")) == "msg1"

    async def test_hash(self):
        assert hash(exceptions.ErrorDetail("msg")) == hash("msg")
        assert hash(exceptions.ErrorDetail("msg", "code")) == hash("msg")


async def test_server_error():
    request = RequestFactory().get("/")
    response = exceptions.server_error(request)
    assert response.status_code == 500
    assert response["content-type"] == "application/json"


async def test_bad_request():
    request = RequestFactory().get("/")
    exception = Exception("Something went wrong — Not used")
    response = exceptions.bad_request(request, exception)
    assert response.status_code == 400
    assert response["content-type"] == "application/json"


async def test_exception_with_list_details():
    res = await client.get("list_exception")
    assert res.status_code == 500
    assert res.json()["data"] == {
        "detail": "[ErrorDetail(string='some error 1', code='error'), "
        "ErrorDetail(string='some error 2', code='error')]",
    }


async def test_exception_with_list_full_details():
    res = await client.get("list_exception_full_detail")
    assert res.status_code == 200
    assert res.json()["data"] == [
        {"message": "some error 1", "code": "error"},
        {"message": "some error 2", "code": "error"},
    ]


async def test_exception_with_dict_details():
    res = await client.get("dict_exception")
    assert res.status_code == 500
    assert res.json()["data"] == {
        "detail": "{'error': ErrorDetail(string='error 1', code='error')}"
    }


async def test_exception_with_full_details():
    res = await client.get("dict_exception_full_detail")
    assert res.status_code == 200
    assert res.json()["data"] == {"error": {"message": "error 1", "code": "error"}}


async def test_exception_dict_exception_code_detail():
    res = await client.get("dict_exception_code_detail")
    assert res.status_code == 200
    assert res.json()["data"] == {"error": "error"}


async def test_exception_with_list_exception_code_detail():
    res = await client.get("list_exception_code_detail")
    assert res.status_code == 200
    assert res.json()["data"] == ["error"]


def test_validation_error():
    exception = exceptions.ValidationError()
    assert exception.detail == [
        exceptions.ErrorDetail(
            string=exceptions.ValidationError.default_detail,
            code=exceptions.ValidationError.default_code,
        )
    ]
    assert exception.get_codes() == [exceptions.ValidationError.default_code]

    exception = exceptions.ValidationError(["errors"])
    assert exception.detail == ["errors"]


def test_method_not_allowed_error():
    exception = exceptions.MethodNotAllowed("get")
    assert exception.detail == exceptions.MethodNotAllowed.default_detail.format(
        method="get"
    )
    assert exception.get_codes() == exceptions.MethodNotAllowed.default_code

    exception = exceptions.MethodNotAllowed("get", ["errors"])
    assert exception.detail == ["errors"]


async def test_method_not_allowed_accepted_error():
    exception = exceptions.NotAcceptable()
    assert exception.detail == exceptions.NotAcceptable.default_detail
    assert exception.get_codes() == exceptions.NotAcceptable.default_code

    exception = exceptions.NotAcceptable(["errors"])
    assert exception.detail == ["errors"]


async def test_unsupported_media_type_allowed_error():
    exception = exceptions.UnsupportedMediaType("whatever/type")
    assert exception.detail == exceptions.UnsupportedMediaType.default_detail.format(
        media_type="whatever/type"
    )
    assert exception.get_codes() == exceptions.UnsupportedMediaType.default_code

    exception = exceptions.UnsupportedMediaType("whatever/type", ["errors"])
    assert exception.detail == ["errors"]


async def test_api_exception_code():
    exception = APIAuthException("Unexpected error")
    assert exception.detail == "Unexpected error"
    assert exception.status_code == 401


api_default = EasyAPI(urls_namespace="exception_default", easy_output=False)


@api_default.get("/list_exception")
async def list_exception_default(request):
    raise BaseAPIException(
        [
            "some error 1",
            "some error 2",
        ]
    )


client_default = testing.EasyTestClient(api_default)


async def test_exception_with_list_details_default():
    res = await client_default.get("list_exception")
    assert res.status_code == 500
    assert res.json() == {
        "detail": "[ErrorDetail(string='some error 1', code='error'), "
        "ErrorDetail(string='some error 2', code='error')]",
    }
