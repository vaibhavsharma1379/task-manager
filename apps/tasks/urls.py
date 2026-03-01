"""
Task URL routing via DRF's DefaultRouter.

The router auto-generates:
  GET    /api/tasks/          -> TaskViewSet.list
  POST   /api/tasks/          -> TaskViewSet.create
  GET    /api/tasks/{id}/     -> TaskViewSet.retrieve
  PUT    /api/tasks/{id}/     -> TaskViewSet.update
  PATCH  /api/tasks/{id}/     -> TaskViewSet.partial_update
  DELETE /api/tasks/{id}/     -> TaskViewSet.destroy
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TaskViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("", include(router.urls)),
]
