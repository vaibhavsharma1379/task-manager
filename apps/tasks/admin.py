from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "completed", "created_at", "updated_at")
    list_filter = ("completed", "created_at")
    search_fields = ("title", "description", "user__email")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("user",)  # efficient FK selector for large user tables
