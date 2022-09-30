import json

import django
import pytest
from asgiref.sync import sync_to_async

from tests.demo_app.models import Event
from tests.demo_app.schema import EventSchema
from tests.demo_app.controllers import (
    EasyEventPermissionController,
    EventControllerAPI,
    EventPermissionController,
)
from tests.demo_app.tests.test_async_crud_apis import dummy_data


@pytest.mark.skipif(django.VERSION < (3, 1), reason="requires django 3.1 or higher")
@pytest.mark.django_db
class TestEasyEventPermissionController:
    async def test_demo(self, easy_async_client):
        client = easy_async_client(EasyEventPermissionController)

        response = await client.get(
            "/must_be_authenticated?word=authenticated", content_type="application/json"
        )
        assert response.status_code == 200
        assert response.json().get("data")["says"] == "authenticated"

        client = easy_async_client(EasyEventPermissionController)
        response = await client.get(
            "/must_be_admin_user?word=admin",
        )
        assert response.status_code == 200
        with pytest.raises(KeyError):
            assert response.json().get("data")["says"] == "admin"

        client = easy_async_client(EasyEventPermissionController, is_staff=True)
        response = await client.get(
            "/must_be_admin_user?word=admin",
        )
        assert response.status_code == 200
        assert response.json().get("data")["says"] == "admin"

        client = easy_async_client(EasyEventPermissionController)
        response = await client.get(
            "/must_be_super_user?word=superuser",
        )
        assert response.status_code == 200
        with pytest.raises(KeyError):
            assert response.json().get("data")["says"] == "superuser"

        client = easy_async_client(EasyEventPermissionController, is_superuser=True)
        response = await client.get(
            "/must_be_super_user?word=superuser",
        )
        assert response.status_code == 200
        assert response.json().get("data")["says"] == "superuser"

    async def test_perm(self, transactional_db, easy_async_client):
        client = easy_async_client(EasyEventPermissionController)
        response = await client.get("/test_perm", query=dict(word="normal"))
        assert response.status_code == 200
        assert response.json().get("data") == {
            "detail": "You do not have permission to perform this action."
        }
        client = easy_async_client(EasyEventPermissionController, is_staff=True)
        response = await client.get("/test_perm", query=dict(word="staff"))
        assert response.status_code == 200
        assert response.json().get("data")["says"] == "staff"

    async def test_perm_only_super(self, transactional_db, easy_async_client):
        client = easy_async_client(EasyEventPermissionController)
        response = await client.get("/test_perm_only_super")
        assert response.status_code == 200
        assert response.json().get("data") == {
            "detail": "You do not have permission to perform this action."
        }

        client = easy_async_client(EasyEventPermissionController)
        response = await client.get("/test_perm_only_super")
        assert response.status_code == 200
        assert response.json().get("data") == {
            "detail": "You do not have permission to perform this action."
        }

        client = easy_async_client(EasyEventPermissionController, is_superuser=True)
        response = await client.get("/test_perm_only_super")
        assert response.status_code == 200
        assert response.json().get("data")["title"] == "test_event_title"


@pytest.mark.skipif(django.VERSION < (3, 1), reason="requires django 3.1 or higher")
@pytest.mark.django_db
class TestEventBasePermissionController:
    async def test_crud_default_get_delete(
        self, transactional_db, easy_admin_async_client
    ):
        client = easy_admin_async_client(EventControllerAPI)

        object_data = dummy_data.copy()
        object_data.update(title=f"{object_data['title']}_get")

        event = await sync_to_async(Event.objects.create)(**object_data)

        response = await client.get(
            f"/?id={event.id}",
        )
        assert response.status_code == 200

        data = response.json().get("data")
        assert data["title"] == "AsyncAPIEvent_get"

        event_schema = json.loads(EventSchema.from_orm(event).json())
        assert event_schema["end_date"] == data["end_date"]

        client = easy_admin_async_client(EventControllerAPI, is_superuser=True)

        await client.delete(
            f"/?id={event.id}",
        )

        response = await client.get(
            f"/?id={event.id}",
        )
        assert response.status_code == 200
        assert response.json().get("data") == {}


@pytest.mark.skipif(django.VERSION < (3, 1), reason="requires django 3.1 or higher")
@pytest.mark.django_db
class TestEventPermissionController:
    async def test_demo(self, transactional_db, easy_async_client):
        client = easy_async_client(EventPermissionController)

        response = await client.get(
            "/must_be_authenticated?word=authenticated", content_type="application/json"
        )
        assert response.status_code == 200
        assert response.json().get("data")["says"] == "authenticated"

        client = easy_async_client(EasyEventPermissionController, is_staff=True)
        response = await client.get(
            "/must_be_admin_user?word=admin",
        )
        assert response.status_code == 200
        assert response.json().get("data")["says"] == "admin"
