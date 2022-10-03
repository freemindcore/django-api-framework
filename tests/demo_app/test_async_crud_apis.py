from datetime import datetime, timedelta

import django
import pytest

from tests.demo_app.controllers import EventEasyControllerAPI
from tests.demo_app.services import EventService

dummy_data = dict(
    title="AsyncAPIEvent",
    start_date=str(datetime.now().date()),
    end_date=str((datetime.now() + timedelta(days=5)).date()),
)


@pytest.mark.skipif(django.VERSION < (3, 1), reason="requires django 3.1 or higher")
@pytest.mark.django_db
class TestEventEasyControllerAPI:
    async def test_crud_default_create(self, transactional_db, easy_api_client):
        client = easy_api_client(EventEasyControllerAPI)

        object_data = await EventService.prepare_create_event_data(dummy_data)

        response = await client.put(
            "/", json=object_data, content_type="application/json"
        )
        assert response.status_code == 200

        event_id = response.json().get("data")["id"]

        response = await client.get(
            f"/?id={event_id}",
        )
        assert response.status_code == 200
        assert response.json().get("data")["title"] == "AsyncAPIEvent_create"

        response = await client.get("/list")
        assert response.status_code == 200
        assert response.json().get("data")[0]["title"] == "AsyncAPIEvent_create"

    async def test_dummy(self, transactional_db, easy_api_client):
        client = easy_api_client(EventEasyControllerAPI)

        response = await client.get(
            "/dummy",
        )
        assert response.status_code == 200
        assert response.json().get("data")["data"] == 1

    async def test_get_objs(self, transactional_db, easy_api_client):
        client = easy_api_client(EventEasyControllerAPI)

        object_data = await EventService.prepare_create_event_data(dummy_data)

        response = await client.put(
            "/", json=object_data, content_type="application/json"
        )
        assert response.status_code == 200

        event_id = response.json().get("data")["id"]

        response = await client.get(
            "/get_objs",
        )
        assert response.status_code == 200
        assert response.json().get("data")[0]["id"] == event_id
