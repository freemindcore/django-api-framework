from datetime import datetime, timedelta

import django
import pytest
from asgiref.sync import sync_to_async

from tests.demo_app.controllers import (
    AdminSitePermissionAPIController,
    AutoGenCrudAPIController,
    PermissionAPIController,
)
from tests.demo_app.models import Client, Event
from tests.demo_app.test_async_other_apis import dummy_data


@pytest.mark.skipif(django.VERSION < (3, 1), reason="requires django 3.1 or higher")
@pytest.mark.django_db
class TestPermissionController:
    async def test_demo(self, easy_api_client):
        client = easy_api_client(PermissionAPIController)

        response = await client.get(
            "/must_be_authenticated/?word=authenticated",
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json().get("data")["says"] == "authenticated"

        client = easy_api_client(PermissionAPIController)
        response = await client.get(
            "/must_be_admin_user/?word=admin",
        )
        assert response.status_code == 403
        with pytest.raises(KeyError):
            assert response.json().get("data")["says"] == "admin"

        client = easy_api_client(PermissionAPIController, is_staff=True)
        response = await client.get(
            "/must_be_admin_user/?word=admin",
        )
        assert response.status_code == 200
        assert response.json().get("data")["says"] == "admin"

        client = easy_api_client(PermissionAPIController)
        response = await client.get(
            "/must_be_super_user/?word=superuser",
        )
        assert response.status_code == 403
        with pytest.raises(KeyError):
            assert response.json().get("data")["says"] == "superuser"

        client = easy_api_client(PermissionAPIController, is_superuser=True)
        response = await client.get(
            "/must_be_super_user/?word=superuser",
        )
        assert response.status_code == 200
        assert response.json().get("data")["says"] == "superuser"

    async def test_perm(self, transactional_db, easy_api_client):
        client = easy_api_client(PermissionAPIController)
        response = await client.get("/test_perm/", query=dict(word="normal"))
        assert response.status_code == 200
        assert response.json().get("data")["says"] == "normal"
        client = easy_api_client(PermissionAPIController, is_staff=True)
        response = await client.get("/test_perm/", query=dict(word="staff"))
        assert response.status_code == 200
        assert response.json().get("data")["says"] == "staff"

    async def test_perm_only_super(self, transactional_db, easy_api_client):
        client = easy_api_client(PermissionAPIController)
        response = await client.get("/test_perm_only_super/")
        assert response.status_code == 403
        assert response.json().get("data") == {
            "detail": "You do not have permission to perform this action."
        }

        client = easy_api_client(PermissionAPIController)
        response = await client.get("/test_perm_only_super/")
        assert response.status_code == 403
        assert response.json().get("data") == {
            "detail": "You do not have permission to perform this action."
        }

        client = easy_api_client(PermissionAPIController, is_superuser=True)
        response = await client.get("/test_perm_only_super/")
        assert response.status_code == 200
        assert response.json().get("data")["title"] == "test_event_title"

    async def test_perm_admin_site(self, transactional_db, easy_api_client):
        # None-admin users
        client = easy_api_client(PermissionAPIController)
        response = await client.get(
            "/test_perm_admin_site/", query=dict(word="non-admin")
        )
        assert response.status_code == 403
        assert response.json().get("data") == {
            "detail": "You do not have permission to perform this action."
        }

        # Staff users
        client = easy_api_client(PermissionAPIController, is_staff=True)
        response = await client.get("/test_perm_admin_site/", query=dict(word="staff"))
        assert response.status_code == 200
        assert response.json()["data"]["says"] == "staff"

    async def test_perm_auto_apis_delete(self, transactional_db, easy_api_client):
        client = easy_api_client(AdminSitePermissionAPIController)
        # Test delete
        object_data = dummy_data.copy()
        object_data.update(title=f"{object_data['title']}_get")
        event = await sync_to_async(Event.objects.create)(**object_data)
        response = await client.get(
            f"/{event.id}",
        )
        assert response.status_code == 403

        response = await client.delete(
            f"/{event.id}",
        )
        assert response.status_code == 403
        assert response.json().get("data") == {
            "detail": "You do not have permission to perform this action."
        }

        # Super users
        client = easy_api_client(AutoGenCrudAPIController, is_superuser=True)
        await client.delete(
            f"/{event.id}",
        )

        response = await client.get(
            f"/{event.id}",
        )
        assert response.status_code == 200
        assert response.json().get("code") == 404

    async def test_perm_auto_apis_patch(self, transactional_db, easy_api_client):
        client = easy_api_client(AdminSitePermissionAPIController)

        object_data = dummy_data.copy()
        event = await sync_to_async(Event.objects.create)(**object_data)

        response = await client.get(
            f"/{event.id}",
        )
        assert response.status_code == 403
        assert response.json().get("data") == {
            "detail": "You do not have permission to perform this action."
        }

        # Staff users
        client = easy_api_client(AutoGenCrudAPIController, is_staff=True)
        response = await client.get(
            f"/{event.id}",
        )
        assert response.json().get("data")["title"] == f"{object_data['title']}"

        client_g = await sync_to_async(Client.objects.create)(
            name="Client G for Unit Testings", key="G"
        )

        client_h = await sync_to_async(Client.objects.create)(
            name="Client H for Unit Testings", key="H"
        )

        new_data = dict(
            id=event.id,
            title=f"{object_data['title']}_patch",
            start_date=str((datetime.now() + timedelta(days=10)).date()),
            end_date=str((datetime.now() + timedelta(days=20)).date()),
            owner=[client_g.id, client_h.id],
        )

        client = easy_api_client(AdminSitePermissionAPIController)
        response = await client.patch(
            f"/{event.id}", json=new_data, content_type="application/json"
        )

        assert response.status_code == 403
        assert response.json().get("data") == {
            "detail": "You do not have permission to perform this action."
        }

        # Super users
        client = easy_api_client(AutoGenCrudAPIController, is_superuser=True)
        response = await client.patch(
            f"/{event.id}", json=new_data, content_type="application/json"
        )
        assert response.json().get("data")

        response = await client.get(
            f"/{event.id}",
        )
        assert response.status_code == 200
        assert response.json().get("data")["title"] == "AsyncAPIEvent_patch"
        assert response.json().get("data")["start_date"] == str(
            (datetime.now() + timedelta(days=10)).date()
        )
        assert response.json().get("data")["end_date"] == str(
            (datetime.now() + timedelta(days=20)).date()
        )
