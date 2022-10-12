from unittest.mock import Mock

from ninja.openapi.urls import get_openapi_urls

from easy import EasyAPI
from easy.decorators import docs_permission_required


def test_docs_decorator_staff_members():
    api = EasyAPI(docs_decorator=docs_permission_required)
    paths = get_openapi_urls(api)

    assert len(paths) == 2
    for ptrn in paths:
        request = Mock(user=Mock(is_staff=True))
        result = ptrn.callback(request)
        assert result.status_code == 200

        request = Mock(user=Mock(is_staff=False))
        request.build_absolute_uri = lambda: "http://example.com"
        result = ptrn.callback(request)
        assert result.status_code == 302
