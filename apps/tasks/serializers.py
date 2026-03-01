"""
Task serializers.

TaskSerializer handles all CRUD operations.
`user` and timestamp fields are read-only — they are set server-side,
not accepted from request bodies. This prevents users from assigning
tasks to other users.
"""

from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    # Nest a small user summary so consumers know who owns each task
    owner = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "owner",
            "title",
            "description",
            "completed",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "owner", "created_at", "updated_at")

    def get_owner(self, obj) -> dict:
        return {
            "id": obj.user.id,
            "email": obj.user.email,
            "username": obj.user.username,
        }

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be blank.")
        return value.strip()
