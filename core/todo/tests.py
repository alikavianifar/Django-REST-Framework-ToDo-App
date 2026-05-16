import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import Profile
from todo.models import Task

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    return User.objects.create_user(
        email="test@test.com",
        password="StrongPassword123!",
        username="testuser",
        is_verified=True,
    )


@pytest.mark.django_db
class TestTodoAPI:
    def test_get_tasks_unauthorized(self, api_client):
        response = api_client.get(reverse("todo:api-v1:todo-list"))
        assert response.status_code == 401

    def test_get_tasks_authorized(self, api_client, create_user):
        api_client.force_authenticate(user=create_user)
        response = api_client.get(reverse("todo:api-v1:todo-list"))
        assert response.status_code == 200

    def test_create_task(self, api_client, create_user):
        api_client.force_authenticate(user=create_user)
        response = api_client.post(
            reverse("todo:api-v1:todo-list"),
            {
                "title": "Test Task",
                "description": "This is a test task",
                "priority": "high",
            },
        )
        assert response.status_code == 201
        assert Task.objects.count() == 1
        assert Task.objects.first().author.user == create_user

    def test_user_cannot_see_others_tasks_in_list(self, api_client, create_user):
        other_user = User.objects.create_user(
            email="other@test.com",
            password="StrongPassword123!",
            username="otheruser",
            is_verified=True,
        )
        other_profile = Profile.objects.get(user=other_user)
        Task.objects.create(author=other_profile, title="Other's Task", priority="low")

        api_client.force_authenticate(user=create_user)
        response = api_client.get(reverse("todo:api-v1:todo-list"))
        assert response.status_code == 200
        assert response.data["total_objects"] == 0

    def test_user_cannot_retrieve_others_task(self, api_client, create_user):
        other_user = User.objects.create_user(
            email="other2@test.com",
            password="StrongPassword123!",
            username="otheruser2",
            is_verified=True,
        )
        other_profile = Profile.objects.get(user=other_user)
        task = Task.objects.create(
            author=other_profile, title="Secret Task", priority="low"
        )

        api_client.force_authenticate(user=create_user)
        url = reverse("todo:api-v1:todo-detail", kwargs={"pk": task.pk})
        response = api_client.get(url)
        assert response.status_code == 404

    def test_delete_task(self, api_client, create_user):
        api_client.force_authenticate(user=create_user)
        profile = Profile.objects.get(user=create_user)
        task = Task.objects.create(author=profile, title="To Delete", priority="low")
        url = reverse("todo:api-v1:todo-detail", kwargs={"pk": task.pk})
        response = api_client.delete(url)
        assert response.status_code == 204
        assert Task.objects.count() == 0
