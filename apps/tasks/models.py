"""
Task model.

Design decisions:
  - ForeignKey to settings.AUTH_USER_MODEL (not a hardcoded import) so this
    works regardless of where the User model lives.
  - on_delete=CASCADE: deleting a user removes all their tasks. This is the
    correct behaviour for owned resources — no orphaned rows.
  - auto_now_add / auto_now handle timestamps automatically at the DB level.
  - default ordering by -created_at so newest tasks appear first in API lists.
"""

from django.conf import settings
from django.db import models


class Task(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tasks"
        ordering = ["-created_at"]
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        status = "✓" if self.completed else "○"
        return f"[{status}] {self.title}"
