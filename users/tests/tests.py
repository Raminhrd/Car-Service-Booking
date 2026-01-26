import pytest

from django.core.cache import cache
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()
pytestmark = pytest.mark.django_db


class TestOTPAuth:
    def test_otp_request_stores_otp_and_calls_celery(self, api_client, monkeypatch):
        phone = "+989121234567"
        fixed_otp = "1234"

        # Mock OTP generator
        monkeypatch.setattr("users.views.generate_otp", lambda length=4: fixed_otp)

        # Mock celery delay
        called = {"ok": False, "args": None}

        def fake_delay(p, o):
            called["ok"] = True
            called["args"] = (p, o)

        monkeypatch.setattr("users.views.send_otp_sms.delay", fake_delay)

        res = api_client.post(
            "/users/otp/request/",
            data={"phone_number": phone},
            format="json"
        )

        assert res.status_code == 200
        assert cache.get(f"otp_{phone}") == fixed_otp
        assert called["ok"] is True
        assert called["args"] == (phone, fixed_otp)

    def test_otp_login_sets_cookies_and_deletes_cache(self, api_client):
        phone = "+989121234567"
        otp = "1234"

        User.objects.create_user(phone_number=phone, password="x12345678")
        cache.set(f"otp_{phone}", otp, timeout=120)

        res = api_client.post(
            "/users/otp/login/",
            data={"phone_number": phone, "otp": otp},
            format="json"
        )

        assert res.status_code == 200
        assert cache.get(f"otp_{phone}") is None
        assert "accessToken" in res.cookies
        assert "refreshToken" in res.cookies


class TestUserInfo:
    def test_user_info_returns_data(self, api_client):
        user = User.objects.create_user(phone_number="+989121234567", password="x12345678")

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        api_client.cookies["accessToken"] = access

        res = api_client.get("/users/info/")

        assert res.status_code == 200
        assert res.json()["phone_number"] == "+989121234567"
