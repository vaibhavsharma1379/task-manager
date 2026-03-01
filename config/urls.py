"""
Root URL configuration.
All API routes live under /api/.
Swagger UI is available at /api/docs/.
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # Authentication endpoints  (register, login, logout, token refresh)
    path("api/auth/", include("apps.users.urls")),

    # Task CRUD endpoints
    path("api/", include("apps.tasks.urls")),

    # OpenAPI schema (machine-readable JSON)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),

    # Swagger UI (interactive browser)
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

    # ReDoc UI (alternative docs browser)
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
