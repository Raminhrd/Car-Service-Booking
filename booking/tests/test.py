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
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and "results" in payload and isinstance(payload["results"], list):
        return payload["results"]
    raise AssertionError(f"Unexpected response shape: {payload}")


def make_user(phone="+989121111111"):
    return User.objects.create_user(phone_number=phone, password="x12345678")


def make_category(name="Sedan"):
    return Category.objects.create(name=name, is_active=True)


def make_car(owner, category, name="MyCar", pelak="11A111", vin="VIN111", model_year=2022):
    return Car.objects.create(
        owner=owner,
        category=category,
        name=name,
        pelak=pelak,
        vin=vin,
        model_year=model_year,
    )


def make_service(title="Detailing", service_type=None, minutes=45):
    # اگر اسم choices تو مدل Service فرق داره، اینجا فقط همین خط رو تغییر بده
    if service_type is None:
        service_type = Service.Type.Detailing
    return Service.objects.create(
        title=title,
        service_type=service_type,
        is_active=True,
        base_duration_minutes=minutes,
    )


class TestBookingEndpoints:
    def test_list_returns_only_own_bookings(self, api_client):
        user1 = make_user("+989121111111")
        user2 = make_user("+989122222222")

        cat = make_category()
        car1 = make_car(owner=user1, category=cat, name="Car1", pelak="11A111", vin="VIN111", model_year=2020)
        car2 = make_car(owner=user2, category=cat, name="Car2", pelak="22A222", vin="VIN222", model_year=2021)

        service = make_service(title="Detailing", service_type=Service.Type.Detailing, minutes=45)

        now = timezone.now()
        b1 = Booking.objects.create(
            user=user1,
            car=car1,
            service=service,
            start_at=now + timezone.timedelta(days=1),
            duration_minutes=45,
        )
        Booking.objects.create(
            user=user2,
            car=car2,
            service=service,
            start_at=now + timezone.timedelta(days=2),
            duration_minutes=45,
        )

        client = auth_client(api_client, user1)
        res = client.get(reverse("book-list"))

        assert res.status_code == 200
        items = extract_items(res.json())

        assert len(items) == 1
        assert items[0]["id"] == b1.id

    def test_cannot_book_for_other_users_car(self, api_client):
        user1 = make_user("+989121111111")
        user2 = make_user("+989122222222")

        cat = make_category()
        other_car = make_car(owner=user2, category=cat, name="OtherCar", pelak="33A333", vin="VIN333", model_year=2019)

        service = make_service(title="Periodic", service_type=Service.Type.Periodic, minutes=30)

        client = auth_client(api_client, user1)
        payload = {
            "car": other_car.id,
            "service": service.id,
            "start_at": (timezone.now() + timezone.timedelta(days=1)).isoformat(),
            "duration_minutes": 30,
            "note": "test",
        }

        res = client.post(reverse("book-list"), data=payload, format="json")
        assert res.status_code == 400
        # اگر خواستی دقیق‌تر:
        # assert "car" in res.json()

    def test_overlapping_booking_is_rejected(self, api_client):
        user = make_user("+989121111111")
        cat = make_category()
        car = make_car(owner=user, category=cat, name="MyCar", pelak="44A444", vin="VIN444", model_year=2022)

        service = make_service(title="Mechanical", service_type=Service.Type.Mechanical, minutes=60)

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

        res = client.post(reverse("book-list"), data=payload, format="json")
        assert res.status_code == 400

    def test_non_overlapping_booking_is_accepted(self, api_client):
        user = make_user("+989121111111")
        cat = make_category()
        car = make_car(owner=user, category=cat, name="MyCar", pelak="55A555", vin="VIN555", model_year=2022)

        service = make_service(title="Detailing", service_type=Service.Type.Detailing, minutes=45)

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

        res = client.post(reverse("book-list"), data=payload, format="json")
        assert res.status_code == 201

        body = res.json()
        assert body["car"] == car.id
        assert body["service"] == service.id
