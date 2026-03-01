"""
Task CRUD + permissions + filtering + pagination tests.
"""

import pytest
from .factories import TaskFactory, CompletedTaskFactory


TASKS_URL = "/api/tasks/"


def task_detail_url(task_id):
    return f"/api/tasks/{task_id}/"


# ---------------------------------------------------------------------------
# List Tasks
# ---------------------------------------------------------------------------

class TestListTasks:
    def test_unauthenticated_can_list_tasks(self, api_client, db):
        TaskFactory.create_batch(3)
        response = api_client.get(TASKS_URL)
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_authenticated_user_sees_only_own_tasks(self, auth_client, user, other_user, db):
        # Create 2 tasks for `user` and 1 for `other_user`
        TaskFactory.create_batch(2, user=user)
        TaskFactory(user=other_user)

        response = auth_client.get(TASKS_URL)

        assert response.status_code == 200
        results = response.json()["data"]["results"]
        assert len(results) == 2
        for item in results:
            assert item["owner"]["id"] == user.id

    def test_admin_sees_all_tasks(self, admin_client, user, other_user, admin_user, db):
        TaskFactory(user=user)
        TaskFactory(user=other_user)
        TaskFactory(user=admin_user)

        response = admin_client.get(TASKS_URL)

        assert response.status_code == 200
        count = response.json()["data"]["count"]
        assert count == 3

    def test_response_is_paginated(self, api_client, db):
        TaskFactory.create_batch(15)
        response = api_client.get(TASKS_URL)

        assert response.status_code == 200
        data = response.json()["data"]
        assert "count" in data
        assert "next" in data
        assert "previous" in data
        assert "results" in data
        assert len(data["results"]) == 10  # default page size

    def test_custom_page_size(self, api_client, db):
        TaskFactory.create_batch(10)
        response = api_client.get(TASKS_URL + "?page_size=3")

        assert response.status_code == 200
        assert len(response.json()["data"]["results"]) == 3


# ---------------------------------------------------------------------------
# Filter & Search
# ---------------------------------------------------------------------------

class TestFilterTasks:
    def test_filter_by_completed_true(self, auth_client, user, db):
        TaskFactory.create_batch(3, user=user, completed=False)
        CompletedTaskFactory.create_batch(2, user=user)

        response = auth_client.get(TASKS_URL + "?completed=true")

        assert response.status_code == 200
        results = response.json()["data"]["results"]
        assert len(results) == 2
        assert all(r["completed"] for r in results)

    def test_filter_by_completed_false(self, auth_client, user, db):
        TaskFactory.create_batch(3, user=user, completed=False)
        CompletedTaskFactory.create_batch(2, user=user)

        response = auth_client.get(TASKS_URL + "?completed=false")

        assert response.status_code == 200
        results = response.json()["data"]["results"]
        assert len(results) == 3
        assert all(not r["completed"] for r in results)

    def test_filter_by_title_partial_match(self, auth_client, user, db):
        TaskFactory(user=user, title="Fix the login bug")
        TaskFactory(user=user, title="Write unit tests")
        TaskFactory(user=user, title="Fix database issue")

        response = auth_client.get(TASKS_URL + "?title=fix")

        assert response.status_code == 200
        results = response.json()["data"]["results"]
        assert len(results) == 2

    def test_search_across_title_and_description(self, auth_client, user, db):
        TaskFactory(user=user, title="Deploy app", description="Use kubernetes for orchestration")
        TaskFactory(user=user, title="Write docs", description="Normal description")

        response = auth_client.get(TASKS_URL + "?search=kubernetes")

        assert response.status_code == 200
        results = response.json()["data"]["results"]
        assert len(results) == 1
        assert results[0]["title"] == "Deploy app"


# ---------------------------------------------------------------------------
# Create Task
# ---------------------------------------------------------------------------

class TestCreateTask:
    def test_create_task_success(self, auth_client, user, db):
        payload = {"title": "New Task", "description": "Task description"}
        response = auth_client.post(TASKS_URL, payload)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["title"] == "New Task"
        assert data["data"]["owner"]["id"] == user.id
        assert data["data"]["completed"] is False

    def test_create_task_unauthenticated(self, api_client, db):
        response = api_client.post(TASKS_URL, {"title": "Sneaky task"})
        assert response.status_code == 401

    def test_create_task_blank_title(self, auth_client, db):
        response = auth_client.post(TASKS_URL, {"title": "   "})
        assert response.status_code == 400

    def test_create_task_missing_title(self, auth_client, db):
        response = auth_client.post(TASKS_URL, {"description": "No title"})
        assert response.status_code == 400

    def test_create_task_description_optional(self, auth_client, user, db):
        response = auth_client.post(TASKS_URL, {"title": "No description task"})
        assert response.status_code == 201
        assert response.json()["data"]["description"] == ""


# ---------------------------------------------------------------------------
# Retrieve Task
# ---------------------------------------------------------------------------

class TestRetrieveTask:
    def test_retrieve_task_success(self, api_client, task, db):
        response = api_client.get(task_detail_url(task.id))
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == task.id
        assert data["data"]["title"] == task.title

    def test_retrieve_nonexistent_task(self, api_client, db):
        response = api_client.get(task_detail_url(99999))
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Update Task (PUT & PATCH)
# ---------------------------------------------------------------------------

class TestUpdateTask:
    def test_owner_can_update_task(self, auth_client, task, db):
        payload = {"title": "Updated title", "description": "Updated desc", "completed": True}
        response = auth_client.put(task_detail_url(task.id), payload)

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["title"] == "Updated title"
        assert data["completed"] is True

    def test_owner_can_partial_update_task(self, auth_client, task, db):
        response = auth_client.patch(task_detail_url(task.id), {"completed": True})
        assert response.status_code == 200
        assert response.json()["data"]["completed"] is True

    def test_non_owner_cannot_update_task(self, other_auth_client, task, db):
        response = other_auth_client.put(
            task_detail_url(task.id),
            {"title": "Hijacked", "description": "", "completed": False},
        )
        assert response.status_code == 403

    def test_unauthenticated_cannot_update_task(self, api_client, task, db):
        response = api_client.put(
            task_detail_url(task.id),
            {"title": "No auth", "description": "", "completed": False},
        )
        assert response.status_code == 401

    def test_admin_can_update_any_task(self, admin_client, task, db):
        response = admin_client.patch(task_detail_url(task.id), {"completed": True})
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Delete Task
# ---------------------------------------------------------------------------

class TestDeleteTask:
    def test_owner_can_delete_task(self, auth_client, task, db):
        response = auth_client.delete(task_detail_url(task.id))
        assert response.status_code == 204

    def test_non_owner_cannot_delete_task(self, other_auth_client, task, db):
        response = other_auth_client.delete(task_detail_url(task.id))
        assert response.status_code == 403

    def test_unauthenticated_cannot_delete_task(self, api_client, task, db):
        response = api_client.delete(task_detail_url(task.id))
        assert response.status_code == 401

    def test_admin_can_delete_any_task(self, admin_client, task, db):
        response = admin_client.delete(task_detail_url(task.id))
        assert response.status_code == 204

    def test_delete_nonexistent_task(self, auth_client, db):
        response = auth_client.delete(task_detail_url(99999))
        assert response.status_code == 404
