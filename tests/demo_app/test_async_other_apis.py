import json
from datetime import datetime, timedelta

import django
import pytest
from asgiref.sync import sync_to_async

from tests.demo_app.controllers import EasyCrudAPIController
from tests.demo_app.models import Event, Type
from tests.demo_app.schema import EventSchema
from tests.demo_app.services import EventService

dummy_data = dict(
    title="AsyncAPIEvent",
    start_date=str(datetime.now().date()),
    end_date=str((datetime.now() + timedelta(days=5)).date()),
)


@pytest.mark.skipif(django.VERSION < (3, 1), reason="requires django 3.1 or higher")
@pytest.mark.django_db
class TestEasyCrudAPIController:
    async def test_crud_apis(self, transactional_db, easy_api_client):
        client = easy_api_client(EasyCrudAPIController)

        object_data = await EventService.prepare_create_event_data(dummy_data)

        response = await client.put(
            "/", json=object_data, content_type="application/json"
        )
        assert response.status_code == 200

        assert response.json().get("code") == 201
        event_id = response.json().get("data")["id"]

        response = await client.get(
            f"/{event_id}",
        )
        assert response.status_code == 200
        assert response.json().get("data")["title"] == "AsyncAPIEvent_create"

        response = await client.get("/")
        assert response.status_code == 200
        assert response.json().get("data")[0]["title"] == "AsyncAPIEvent_create"

    async def test_base_response(self, transactional_db, easy_api_client):
        client = easy_api_client(EasyCrudAPIController)

        response = await client.get(
            "/base_response/",
        )
        assert response.status_code == 200
        assert response.json().get("data")["data"] == "This is a BaseApiResponse."

    async def test_qs_paginated(self, transactional_db, easy_api_client):
        client = easy_api_client(EasyCrudAPIController)

        object_data = await EventService.prepare_create_event_data(dummy_data)

        response = await client.put(
            "/", json=object_data, content_type="application/json"
        )
        assert response.status_code == 200
        assert response.json().get("code") == 201
        event_id = response.json().get("data")["id"]
        response = await client.get(
            "/qs_paginated/",
        )
        assert response.status_code == 200
        assert response.json().get("data")[0]["id"] == event_id

    async def test_qs_list(self, transactional_db, easy_api_client):
        client = easy_api_client(EasyCrudAPIController)

        for i in range(4):
            type = await sync_to_async(Type.objects.create)(name=f"Test-Type-{i}")
            object_data = await EventService.prepare_create_event_data(dummy_data)
            object_data.update(
                title=f"{object_data['title']}_qs_list_{i}", type=type.id
            )
            await client.put("/", json=object_data)

        type = await sync_to_async(Type.objects.create)(name="Test-Type-88")
        object_data = await EventService.prepare_create_event_data(dummy_data)
        object_data.update(title=f"{object_data['title']}_qs_list_88", type=type)
        event = await sync_to_async(Event.objects.create)(**object_data)

        response = await client.get(
            "/qs_list/",
        )
        assert response.status_code == 200

        data = response.json().get("data")

        assert data[0]["title"] == "AsyncAPIEvent_create_qs_list_0"

        event_schema = json.loads(EventSchema.from_orm(event).json())
        assert (
            event_schema["title"]
            == data[4]["title"]
            == "AsyncAPIEvent_create_qs_list_88"
        )

    async def test_qs_(self, transactional_db, easy_api_client):
        client = easy_api_client(EasyCrudAPIController)

        for i in range(4):
            type = await sync_to_async(Type.objects.create)(name=f"Test-Type-{i}")
            object_data = await EventService.prepare_create_event_data(dummy_data)
            object_data.update(title=f"{object_data['title']}_qs_{i}", type=type.id)
            await client.put("/", json=object_data)

        response = await client.get(
            "/qs/",
        )
        assert response.status_code == 200

        assert response.json().get("data")[0]["title"] == "AsyncAPIEvent_create_qs_0"
