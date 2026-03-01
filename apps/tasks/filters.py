"""
FilterSet for Task list queries.

Supported query parameters:
  ?completed=true          filter by completion status
  ?completed=false
  ?title=keyword           case-insensitive partial match on title
  ?search=keyword          full-text search across title + description (SearchFilter)
  ?ordering=created_at     sort ascending
  ?ordering=-created_at    sort descending (default)
"""

from django_filters import rest_framework as filters
from .models import Task


class TaskFilter(filters.FilterSet):
    completed = filters.BooleanFilter(field_name="completed")
    title = filters.CharFilter(field_name="title", lookup_expr="icontains")

    class Meta:
        model = Task
        fields = ["completed", "title"]
