import logging
from abc import ABC
from typing import Any

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from ninja_jwt.authentication import JWTAuth

logger = logging.getLogger(__name__)
user_model = get_user_model()


class JWTAuthAsync(JWTAuth, ABC):
    async def authenticate(self, request: HttpRequest, token: str) -> Any:
        return await sync_to_async(super().authenticate)(request, token)


jwt_auth = JWTAuth()
jwt_auth_async = JWTAuthAsync()
