"""
Page-number pagination for the Task list endpoint.

Consumers can control page size via ?page_size=N (max 100).
The response envelope looks like:
  {
    "count": 42,
    "next": "http://localhost:8000/api/tasks/?page=3",
    "previous": "http://localhost:8000/api/tasks/?page=1",
    "results": [ ... ]
  }
"""

from rest_framework.pagination import PageNumberPagination


class TaskPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100
