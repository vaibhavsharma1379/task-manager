"""
Auth endpoint tests.

Convention:
  - Every test name starts with test_ and describes the scenario precisely.
  - We use `db` marker (via fixtures) to allow DB access.
  - We assert both the HTTP status code AND the response body shape.
"""

import pytest
from django.urls import reverse

from apps.users.models import User
from .factories import UserFactory


REGISTER_URL = "/api/auth/register/"
LOGIN_URL = "/api/auth/login/"
LOGOUT_URL = "/api/auth/logout/"
REFRESH_URL = "/api/auth/token/refresh/"


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

class TestRegister:
    def test_register_success(self, api_client, db):
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "StrongPass1!",
            "password2": "StrongPass1!",
        }
        response = api_client.post(REGISTER_URL, payload)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "tokens" in data["data"]
        assert "access" in data["data"]["tokens"]
        assert "refresh" in data["data"]["tokens"]
        assert data["data"]["user"]["email"] == "new@example.com"
        # Password must never appear in the response
        assert "password" not in data["data"]["user"]

    def test_register_duplicate_email(self, api_client, db):
        UserFactory(email="existing@example.com")
        payload = {
            "username": "another",
            "email": "existing@example.com",
            "password": "StrongPass1!",
            "password2": "StrongPass1!",
        }
        response = api_client.post(REGISTER_URL, payload)

        assert response.status_code == 400
        assert response.json()["success"] is False

    def test_register_password_mismatch(self, api_client, db):
        payload = {
            "username": "mismatch",
            "email": "mismatch@example.com",
            "password": "StrongPass1!",
            "password2": "DifferentPass!",
        }
        response = api_client.post(REGISTER_URL, payload)

        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "password" in data["errors"]

    def test_register_missing_fields(self, api_client, db):
        response = api_client.post(REGISTER_URL, {"email": "incomplete@example.com"})
        assert response.status_code == 400

    def test_register_short_password(self, api_client, db):
        payload = {
            "username": "shortpw",
            "email": "short@example.com",
            "password": "abc",
            "password2": "abc",
        }
        response = api_client.post(REGISTER_URL, payload)
        assert response.status_code == 400


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class TestLogin:
    def test_login_success(self, api_client, db):
        user = UserFactory(email="login@example.com")
        # UserFactory.set_password("testpass123") sets the password

        response = api_client.post(LOGIN_URL, {
            "email": "login@example.com",
            "password": "testpass123",
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access" in data["data"]["tokens"]
        assert "refresh" in data["data"]["tokens"]

    def test_login_wrong_password(self, api_client, db):
        UserFactory(email="wrongpw@example.com")
        response = api_client.post(LOGIN_URL, {
            "email": "wrongpw@example.com",
            "password": "wrongpassword",
        })
        assert response.status_code == 400
        assert response.json()["success"] is False

    def test_login_nonexistent_user(self, api_client, db):
        response = api_client.post(LOGIN_URL, {
            "email": "ghost@example.com",
            "password": "doesntmatter",
        })
        assert response.status_code == 400

    def test_login_missing_fields(self, api_client, db):
        response = api_client.post(LOGIN_URL, {"email": "nopass@example.com"})
        assert response.status_code == 400


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

class TestLogout:
    def test_logout_success(self, api_client, db):
        from rest_framework_simplejwt.tokens import RefreshToken
        user = UserFactory()
        refresh = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = api_client.post(LOGOUT_URL, {"refresh": str(refresh)})

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_logout_requires_authentication(self, api_client, db):
        response = api_client.post(LOGOUT_URL, {"refresh": "sometoken"})
        assert response.status_code == 401

    def test_logout_without_refresh_token(self, auth_client, db):
        response = auth_client.post(LOGOUT_URL, {})
        assert response.status_code == 400

    def test_logout_invalid_refresh_token(self, auth_client, db):
        response = auth_client.post(LOGOUT_URL, {"refresh": "not.a.valid.token"})
        assert response.status_code == 400


# ---------------------------------------------------------------------------
# Token Refresh
# ---------------------------------------------------------------------------

class TestTokenRefresh:
    def test_refresh_returns_new_access_token(self, api_client, db):
        from rest_framework_simplejwt.tokens import RefreshToken
        user = UserFactory()
        refresh = RefreshToken.for_user(user)

        response = api_client.post(REFRESH_URL, {"refresh": str(refresh)})

        assert response.status_code == 200
        assert "access" in response.json()

    def test_refresh_with_invalid_token(self, api_client, db):
        response = api_client.post(REFRESH_URL, {"refresh": "invalid"})
        assert response.status_code == 401
