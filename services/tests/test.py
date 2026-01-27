import pytest
from django.urls import reverse

from services.models import Service

pytestmark = pytest.mark.django_db


def extract_items(payload):

    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if "results" in payload and isinstance(payload["results"], list):
            return payload["results"]
        if "data" in payload and isinstance(payload["data"], list):
            return payload["data"]
    raise AssertionError(f"Unexpected response shape: {payload}")


class TestServiceEndpoints:
    def test_list_services_returns_only_active_services(self, api_client):
        active_service = Service.objects.create(
            title="Periodic Service",
            service_type=Service.Type.Periodic,
            is_active=True,
            base_duration_minutes=30,
        )
        Service.objects.create(
            title="Old Service",
            service_type=Service.Type.Mechanical,
            is_active=False,
            base_duration_minutes=60,
        )

        url = reverse("service-list")
        res = api_client.get(url)
        assert res.status_code == 200

        items = extract_items(res.json())
        assert len(items) == 1
        assert items[0]["id"] == active_service.id

    def test_retrieve_single_service(self, api_client):
        service = Service.objects.create(
            title="Detailing",
            service_type=Service.Type.Detailing,
            is_active=True,
            base_duration_minutes=45,
        )

        url = reverse("service-detail", kwargs={"pk": service.id})
        res = api_client.get(url)

        assert res.status_code == 200
        data = res.json()
        assert data["id"] == service.id
        assert data["title"] == service.title

    def test_create_service_not_allowed(self, api_client):
        url = reverse("service-list")
        res = api_client.post(
            url,
            data={"title": "Hack Service", "service_type": Service.Type.Body},
            format="json",
        )
        assert res.status_code == 405
