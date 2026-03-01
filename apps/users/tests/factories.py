"""
factory_boy factories for User model.

Why factory_boy?
  Instead of calling User.objects.create() manually in every test, factories
  give you a single place to define sensible defaults. Each test can override
  only the fields it cares about, keeping tests focused and concise.
"""

import factory
from factory.django import DjangoModelFactory

from apps.users.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        # Prevent duplicate email conflicts when factory is called multiple times
        django_get_or_create = ("email",)

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    # PostGenerationMethodCall hashes the password properly via set_password()
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    role = User.Role.USER
    is_active = True


class AdminUserFactory(UserFactory):
    """A regular UserFactory but with admin role pre-set."""
    username = factory.Sequence(lambda n: f"admin{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    role = User.Role.ADMIN
