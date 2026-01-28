import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from cars.models import Car, Category
from services.models import Service
from booking.models import Booking

User = get_user_model()
pytestmark = pytest.mark.django_db


def auth_client(api_client, user):
    refresh = RefreshToken.for_user(user)
    api_client.cookies["accessToken"] = str(refresh.access_token)
    return api_client


def extract_items(payload):
    # Works with list or paginated {"results": [...]}
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and "results" in payload and isinstance(payload["results"], list):
        return payload["results"]
    raise AssertionError(f"Unexpected response shape: {payload}")


class TestBookingEndpoints:
    def test_list_returns_only_own_bookings(self, api_client):
        user1 = User.objects.create_user(phone_number="+989121111111", password="x12345678")
        user2 = User.objects.create_user(phone_number="+989122222222", password="x12345678")

        cat = Category.objects.create(name="Sedan", is_active=True)
        car1 = Car.objects.create(owner=user1, category=cat, name="Car1", pelak="11A111", vin="VIN111", model_year=2020)
        car2 = Car.objects.create(owner=user2, category=cat, name="Car2", pelak="22A222", vin="VIN222", model_year=2021)

        service = Service.objects.create(
            title="Detailing",
            service_type=Service.Type.Detailing,
            is_active=True,
            base_duration_minutes=45,
        )

        now = timezone.now()
        b1 = Booking.objects.create(user=user1, car=car1, service=service, start_at=now + timezone.timedelta(days=1), duration_minutes=45)
        Booking.objects.create(user=user2, car=car2, service=service, start_at=now + timezone.timedelta(days=2), duration_minutes=45)

        client = auth_client(api_client, user1)
        res = client.get(reverse("booking-list"))

        assert res.status_code == 200
        items = extract_items(res.json())

        assert len(items) == 1
        assert items[0]["id"] == b1.id

    def test_cannot_book_for_other_users_car(self, api_client):
        user1 = User.objects.create_user(phone_number="+989121111111", password="x12345678")
        user2 = User.objects.create_user(phone_number="+989122222222", password="x12345678")

        cat = Category.objects.create(name="Sedan", is_active=True)
        other_car = Car.objects.create(
            owner=user2, category=cat, name="OtherCar", pelak="33A333", vin="VIN333", model_year=2019
        )

        service = Service.objects.create(
            title="Periodic",
            service_type=Service.Type.Periodic,
            is_active=True,
            base_duration_minutes=30,
        )

        client = auth_client(api_client, user1)
        payload = {
            "car": other_car.id,
            "service": service.id,
            "start_at": (timezone.now() + timezone.timedelta(days=1)).isoformat(),
            "duration_minutes": 30,
            "note": "test",
        }

        res = client.post(reverse("booking-list"), data=payload, format="json")
        assert res.status_code == 400

    def test_overlapping_booking_is_rejected(self, api_client):
        user = User.objects.create_user(phone_number="+989121111111", password="x12345678")
        cat = Category.objects.create(name="Sedan", is_active=True)
        car = Car.objects.create(owner=user, category=cat, name="MyCar", pelak="44A444", vin="VIN444", model_year=2022)

        service = Service.objects.create(
            title="Mechanical",
            service_type=Service.Type.Mechanical,
            is_active=True,
            base_duration_minutes=60,
        )

        start = timezone.now() + timezone.timedelta(days=1, hours=2)

        Booking.objects.create(
            user=user,
            car=car,
            service=service,
            start_at=start,
            duration_minutes=60,
            status=Booking.Status.PENDING,
        )

        client = auth_client(api_client, user)

        payload = {
            "car": car.id,
            "service": service.id,
            "start_at": (start + timezone.timedelta(minutes=30)).isoformat(),
            "duration_minutes": 30,
            "note": "overlap",
        }

        res = client.post(reverse("booking-list"), data=payload, format="json")
        assert res.status_code == 400

    def test_non_overlapping_booking_is_accepted(self, api_client):
        user = User.objects.create_user(phone_number="+989121111111", password="x12345678")
        cat = Category.objects.create(name="Sedan", is_active=True)
        car = Car.objects.create(owner=user, category=cat, name="MyCar", pelak="55A555", vin="VIN555", model_year=2022)

        service = Service.objects.create(
            title="Detailing",
            service_type=Service.Type.Detailing,
            is_active=True,
            base_duration_minutes=45,
        )

        start = timezone.now() + timezone.timedelta(days=1, hours=2)

        Booking.objects.create(
            user=user,
            car=car,
            service=service,
            start_at=start,
            duration_minutes=45,
            status=Booking.Status.CONFIRMED,
        )

        client = auth_client(api_client, user)

        payload = {
            "car": car.id,
            "service": service.id,
            "start_at": (start + timezone.timedelta(minutes=45)).isoformat(),
            "duration_minutes": 30,
            "note": "no overlap",
        }

        res = client.post(reverse("booking-list"), data=payload, format="json")
        assert res.status_code == 201
        body = res.json()
        assert body["car"] == car.id
        assert body["service"] == service.id
