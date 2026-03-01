"""
factory_boy factories for Task model.
"""

import factory
from factory.django import DjangoModelFactory

from apps.tasks.models import Task
from apps.users.tests.factories import UserFactory


class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task

    user = factory.SubFactory(UserFactory)
    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph")
    completed = False


class CompletedTaskFactory(TaskFactory):
    """Convenience factory for already-completed tasks."""
    completed = True
