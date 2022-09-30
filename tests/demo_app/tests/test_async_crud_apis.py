from datetime import datetime, timedelta

import django
import pytest

from tests.demo_app.services import EventService
from tests.demo_app.controllers import (
    EventControllerTest2API,
    EventEasyControllerAPI,
)

dummy_data = dict(
    title="AsyncAPIEvent",
    start_date=str(datetime.now().date()),
    end_date=str((datetime.now() + timedelta(days=5)).date()),
)


@pytest.mark.skipif(django.VERSION < (3, 1), reason="requires django 3.1 or higher")
@pytest.mark.django_db
class TestEventEasyControllerAPI:
    async def test_crud_default_create(self, transactional_db, easy_async_client):
        client = easy_async_client(EventEasyControllerAPI)

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

    async def test_demo(self, transactional_db, easy_async_client):
        client = easy_async_client(EventEasyControllerAPI)

        response = await client.get(
            "/dummy",
        )
        assert response.status_code == 200
        assert response.json().get("data")["data"] == 1


@pytest.mark.skipif(django.VERSION < (3, 1), reason="requires django 3.1 or higher")
@pytest.mark.django_db
class TestEventEasyControllerTest2API:
    async def test_demo(self, transactional_db, easy_async_client):
        client = easy_async_client(EventControllerTest2API)

        object_data = await EventService.prepare_create_event_data(dummy_data)

        response = await client.put(
            "/", json=object_data, content_type="application/json"
        )
        assert response.status_code == 200

        event_id = response.json().get("data")["id"]

        response = await client.get(
            "/demo",
        )
        assert response.status_code == 200
        assert response.json().get("data")[0]["id"] == event_id
