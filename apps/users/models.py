"""
Custom User model.

Why extend AbstractUser instead of AbstractBaseUser?
  AbstractUser already includes username/email/password handling and
  Django's built-in permission system. We just add a `role` field on top.
  AbstractBaseUser is for when you need full control from scratch.

Why set USERNAME_FIELD = 'email'?
  Users log in with their email address, not username, which is more
  intuitive for modern APIs.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        USER = "user", "User"

    # Override email to enforce uniqueness (AbstractUser doesn't do this by default)
    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
    )

    # Use email as the primary login identifier
    USERNAME_FIELD = "email"

    # username is still required when creating via createsuperuser
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

    @property
    def is_admin_role(self) -> bool:
        """Convenience check for the custom role field."""
        return self.role == self.Role.ADMIN
