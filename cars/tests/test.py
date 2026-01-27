import pytest
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from cars.models import Car, Category

User = get_user_model()
pytestmark = pytest.mark.django_db


def auth_client(api_client, user):
    refresh = RefreshToken.for_user(user)
    api_client.cookies["accessToken"] = str(refresh.access_token)
    return api_client


class TestCarEndpoints:
    def test_list_requires_auth(self, api_client):
        res = api_client.get("/cars/my-car/")
        assert res.status_code == 401

    def test_list_returns_only_own_cars(self, api_client):
        user1 = User.objects.create_user(phone_number="+989121111111", password="x12345678")
        user2 = User.objects.create_user(phone_number="+989122222222", password="x12345678")

        cat = Category.objects.create(name="Sedan", is_active=True)

        # user1 cars
        c1 = Car.objects.create(
            name="Car 1",
            owner=user1,
            category=cat,
            pelak="11الف111",
            vin="VIN111",
            model_year=2020,
        )
        c2 = Car.objects.create(
            name="Car 2",
            owner=user1,
            category=cat,
            pelak="22الف222",
            vin="VIN222",
            model_year=2021,
        )

        # user2 car
        Car.objects.create(
            name="Other Car",
            owner=user2,
            category=cat,
            pelak="33الف333",
            vin="VIN333",
            model_year=2019,
        )

        client = auth_client(api_client, user1)
        res = client.get("/cars/my-car/")

        assert res.status_code == 200
        data = res.json()

        items = data["results"] if isinstance(data, dict) and "results" in data else data

        assert len(items) == 2
        returned_ids = {item["id"] for item in items}
        assert returned_ids == {c1.id, c2.id}

    def test_retrieve_other_users_car_returns_404(self, api_client):
        user1 = User.objects.create_user(phone_number="+989121111111", password="x12345678")
        user2 = User.objects.create_user(phone_number="+989122222222", password="x12345678")
        cat = Category.objects.create(name="Sedan", is_active=True)

        other_car = Car.objects.create(
            name="Other Car",
            owner=user2,
            category=cat,
            pelak="33الف333",
            vin="VIN333",
            model_year=2019,
        )

        client = auth_client(api_client, user1)
        res = client.get(f"/cars/my-car/{other_car.id}/")

        # Because queryset is filtered to owner=request.user, it should look "not found"
        assert res.status_code == 404

    def test_delete_own_car_success(self, api_client):
        user = User.objects.create_user(phone_number="+989121111111", password="x12345678")
        cat = Category.objects.create(name="Sedan", is_active=True)

        car = Car.objects.create(
            name="My Car",
            owner=user,
            category=cat,
            pelak="11الف111",
            vin="VIN111",
            model_year=2020,
        )

        client = auth_client(api_client, user)
        res = client.delete(f"/cars/my-car/{car.id}/")

        assert res.status_code in (204, 200)
        assert Car.objects.filter(id=car.id).exists() is False

    def test_delete_other_users_car_returns_404(self, api_client):
        user1 = User.objects.create_user(phone_number="+989121111111", password="x12345678")
        user2 = User.objects.create_user(phone_number="+989122222222", password="x12345678")
        cat = Category.objects.create(name="Sedan", is_active=True)

        other_car = Car.objects.create(
            name="Other Car",
            owner=user2,
            category=cat,
            pelak="33الف333",
            vin="VIN333",
            model_year=2019,
        )

        client = auth_client(api_client, user1)
        res = client.delete(f"/cars/my-car/{other_car.id}/")

        assert res.status_code == 404
        assert Car.objects.filter(id=other_car.id).exists() is True
