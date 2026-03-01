"""
Shared pytest fixtures for the users app tests.
"""

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .factories import UserFactory, AdminUserFactory


@pytest.fixture
def api_client():
    """A plain (unauthenticated) DRF test client."""
    return APIClient()


@pytest.fixture
def user(db):
    """A regular authenticated user."""
    return UserFactory()


@pytest.fixture
def admin_user(db):
    """An admin-role user."""
    return AdminUserFactory()


@pytest.fixture
def auth_client(api_client, user):
    """APIClient pre-authenticated as a regular user via JWT."""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """APIClient pre-authenticated as an admin user."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client
