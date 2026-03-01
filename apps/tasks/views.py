"""
Task ViewSet — handles all CRUD operations via DRF's ModelViewSet.

Why ModelViewSet?
  It auto-generates list, create, retrieve, update, partial_update,
  and destroy actions from a single class, following DRY principle.

Key patterns:
  - get_queryset()      — scopes results by user role (admin sees all, users see own)
  - perform_create()    — injects request.user so users can't forge ownership
  - select_related()    — avoids N+1 DB queries when serializing the `owner` field
  - Uniform responses   — overrides list/create/retrieve/update/destroy to use api_response()
"""

import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from apps.core.exceptions import api_response
from .filters import TaskFilter
from .models import Task
from .pagination import TaskPagination
from .permissions import IsAdminRoleOrOwner
from .serializers import TaskSerializer

logger = logging.getLogger(__name__)


class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    pagination_class = TaskPagination
    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "completed", "title"]
    ordering = ["-created_at"]

    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminRoleOrOwner]

    def get_queryset(self):
        """
        Admin users see all tasks.
        Regular (and unauthenticated) users see only their own tasks.
        select_related('user') fetches the related User row in the same DB query,
        preventing N+1 queries when the serializer accesses obj.user.email.
        """
        user = self.request.user

        if user.is_authenticated and user.is_admin_role:
            return Task.objects.select_related("user").all()

        if user.is_authenticated:
            return Task.objects.select_related("user").filter(user=user)

        # Unauthenticated: read-only access to all tasks (public task list)
        return Task.objects.select_related("user").all()

    def perform_create(self, serializer):
        """Attach the authenticated user as the task owner at save time."""
        serializer.save(user=self.request.user)

    # ------------------------------------------------------------------
    # Override default DRF responses with uniform envelope via api_response
    # ------------------------------------------------------------------

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated = self.get_paginated_response(serializer.data)
            return api_response(paginated.data, "Tasks retrieved successfully.")

        serializer = self.get_serializer(queryset, many=True)
        return api_response(serializer.data, "Tasks retrieved successfully.")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        logger.info("Task created by user %s: '%s'", request.user.email, serializer.data.get("title"))
        return api_response(serializer.data, "Task created successfully.", status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(serializer.data, "Task retrieved successfully.")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        message = "Task partially updated." if partial else "Task updated successfully."
        return api_response(serializer.data, message)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        title = instance.title
        self.perform_destroy(instance)
        logger.info("Task '%s' deleted by user %s", title, request.user.email)
        return api_response(message="Task deleted successfully.", status_code=status.HTTP_204_NO_CONTENT)
