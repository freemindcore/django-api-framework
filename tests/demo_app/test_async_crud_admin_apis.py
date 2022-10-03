import json
from datetime import datetime, timedelta

import django
import pytest
from asgiref.sync import sync_to_async

from tests.demo_app.controllers import EventControllerAdminAPI, EventSchema
from tests.demo_app.models import Event

dummy_data = dict(
    title="AsyncAdminAPIEvent",
    start_date=str(datetime.now().date()),
    end_date=str((datetime.now() + timedelta(days=5)).date()),
)


@pytest.mark.skipif(django.VERSION < (3, 1), reason="requires django 3.1 or higher")
@pytest.mark.django_db
class TestAutoCrudAdminAPI:
    async def test_crud_default_get_all(self, transactional_db, easy_admin_api_client):
        client = easy_admin_api_client(EventControllerAdminAPI)

        object_data = dummy_data.copy()
        object_data.update(title=f"{object_data['title']}_get_all")

        event = await sync_to_async(Event.objects.create)(**object_data)

        response = await client.get(
            "/get_all", query=dict(maximum=100, filters=json.dumps(dict(id__gte=1)))
        )
        assert response.status_code == 200

        data = response.json().get("data")
        assert data[0]["title"] == "AsyncAdminAPIEvent_get_all"

        event_schema = json.loads(EventSchema.from_orm(event).json())
        assert event_schema["start_date"] == data[0]["start_date"]

        response = await client.get(
            "/get_all",
            query=dict(
                maximum=100,
            ),
        )
        assert response.status_code == 200

        data = response.json().get("data")
        assert data[0]["title"] == "AsyncAdminAPIEvent_get_all"

        event_schema = json.loads(EventSchema.from_orm(event).json())
        assert event_schema["start_date"] == data[0]["start_date"]

        response = await client.get("/get_all")
        assert response.status_code == 200

        data = response.json().get("data")
        assert data[0]["title"] == "AsyncAdminAPIEvent_get_all"

        event_schema = json.loads(EventSchema.from_orm(event).json())
        assert event_schema["start_date"] == data[0]["start_date"]

    async def test_crud_default_get_delete(
        self, transactional_db, easy_admin_api_client
    ):
        client = easy_admin_api_client(EventControllerAdminAPI)

        object_data = dummy_data.copy()
        object_data.update(title=f"{object_data['title']}_get")

        event = await sync_to_async(Event.objects.create)(**object_data)

        response = await client.get(
            f"/?id={event.id}",
        )
        assert response.status_code == 200

        data = response.json().get("data")
        assert data["title"] == "AsyncAdminAPIEvent_get"

        event_schema = json.loads(EventSchema.from_orm(event).json())
        assert event_schema["end_date"] == data["end_date"]

        response = await client.delete(
            f"/?id={event.id}",
        )
        assert response.json().get("data") == {
            "detail": "You do not have permission to perform this action."
        }

        client = easy_admin_api_client(EventControllerAdminAPI, is_superuser=True)
        await client.delete(
            f"/?id={event.id}",
        )

        response = await client.get(
            f"/?id={event.id}",
        )
        assert response.status_code == 200
        assert response.json().get("data") == {}

    async def test_crud_default_create(self, transactional_db, easy_admin_api_client):
        client = easy_admin_api_client(EventControllerAdminAPI)

        object_data = dummy_data.copy()
        object_data.update(title=f"{object_data['title']}_create")

        response = await client.put(
            "/", json=object_data, content_type="application/json"
        )
        assert response.status_code == 200

        event_id = response.json().get("data")["id"]

        response = await client.get(
            f"/?id={event_id}",
        )
        assert response.status_code == 200
        assert response.json().get("data")["title"] == "AsyncAdminAPIEvent_create"

    async def test_crud_default_patch(self, transactional_db, easy_admin_api_client):
        client = easy_admin_api_client(EventControllerAdminAPI)

        object_data = dummy_data.copy()
        event = await sync_to_async(Event.objects.create)(**object_data)

        response = await client.get(
            f"/?id={event.id}",
        )
        assert response.status_code == 200
        assert response.json().get("data")["title"] == f"{object_data['title']}"

        new_data = dict(
            id=event.id,
            title=f"{object_data['title']}_patch",
            start_date=str((datetime.now() + timedelta(days=10)).date()),
            end_date=str((datetime.now() + timedelta(days=20)).date()),
        )

        response = await client.patch(
            f"/?id={event.id}", json=new_data, content_type="application/json"
        )

        assert response.status_code == 200
        assert response.json().get("data")["id"] == event.id
        assert response.json().get("data")["created"] is False

        response = await client.get(
            f"/?id={event.id}",
        )
        assert response.status_code == 200
        assert response.json().get("data")["title"] == "AsyncAdminAPIEvent_patch"
        assert response.json().get("data")["start_date"] == str(
            (datetime.now() + timedelta(days=10)).date()
        )
        assert response.json().get("data")["end_date"] == str(
            (datetime.now() + timedelta(days=20)).date()
        )

    async def test_default_filter(self, transactional_db, easy_admin_api_client):
        object_data = dummy_data.copy()
        object_data.update(title=f"{object_data['title']}_filter")

        event = await sync_to_async(Event.objects.create)(**object_data)

        client = easy_admin_api_client(EventControllerAdminAPI)

        response = await client.get(
            "/filter", query=dict(filters=json.dumps(dict(id__gte=1)))
        )
        assert response.status_code == 200

        data = response.json().get("data")
        assert data[0]["title"] == "AsyncAdminAPIEvent_filter"

        event_schema = json.loads(EventSchema.from_orm(event).json())
        assert event_schema["end_date"] == data[0]["end_date"]

    async def test_crud_filter_exclude(self, transactional_db, easy_admin_api_client):
        object_data = dummy_data.copy()
        object_data.update(title=f"{object_data['title']}_exclude")

        event = await sync_to_async(Event.objects.create)(**object_data)

        client = easy_admin_api_client(EventControllerAdminAPI)

        response = await client.get(
            "/filter_exclude", query=dict(filters=json.dumps(dict(id__lt=1)))
        )
        assert response.status_code == 200

        data = response.json().get("data")
        assert data[0]["title"] == "AsyncAdminAPIEvent_exclude"

        event_schema = json.loads(EventSchema.from_orm(event).json())
        assert event_schema["end_date"] == data[0]["end_date"]

    async def test_crud_filter_exclude_paginated(
        self, transactional_db, easy_admin_api_client
    ):
        object_data = dummy_data.copy()
        object_data.update(title=f"{object_data['title']}_exclude_paginated")

        event = await sync_to_async(Event.objects.create)(**object_data)

        client = easy_admin_api_client(EventControllerAdminAPI)

        response = await client.get(
            "/crud_filter_exclude_paginated",
        )
        assert response.status_code == 200

        data = response.json().get("data")
        assert data[0]["title"] == "AsyncAdminAPIEvent_exclude_paginated"

        event_schema = json.loads(EventSchema.from_orm(event).json())
        assert event_schema["end_date"] == data[0]["end_date"]
