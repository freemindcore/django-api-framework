from functools import wraps
from types import FunctionType
from typing import Any, Callable
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpRequest
from django.shortcuts import resolve_url


def request_passes_test(
    test_func: Callable[[Any], Any],
    login_url: str = None,
    redirect_field_name: str = REDIRECT_FIELD_NAME,
) -> Callable[[FunctionType], Callable[[HttpRequest, Any], Any]]:
    """
    Decorator for views that checks that the request passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func: FunctionType) -> Callable[[HttpRequest, Any], Any]:
        @wraps(view_func)
        def _wrapped_view(request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
            if test_func(request):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if (not login_scheme or login_scheme == current_scheme) and (
                not login_netloc or login_netloc == current_netloc
            ):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login

            return redirect_to_login(path, resolved_login_url, redirect_field_name)

        return _wrapped_view

    return decorator


def docs_permission_required(
    view_func: FunctionType = None,
    redirect_field_name: str = REDIRECT_FIELD_NAME,
    login_url: str = "admin:login",
) -> Any:
    """
    Decorator for views that checks that the user is logged in and is a staff
    member, redirecting to the login page if necessary.
    """
    actual_decorator = request_passes_test(
        lambda r: ((r.user.is_active and r.user.is_staff)),
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator  # pragma: no cover
