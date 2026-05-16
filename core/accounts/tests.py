import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient

from accounts.tokens import account_activation_token, password_reset_token
from accounts.utils import PASSWORD_RESET_SENT_MESSAGE

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def verified_user():
    return User.objects.create_user(
        email="test@test.com",
        password="StrongPassword123!",
        username="testuser",
        is_verified=True,
    )


@pytest.fixture
def unverified_user():
    return User.objects.create_user(
        email="unverified@test.com",
        password="StrongPassword123!",
        username="unverified",
        is_verified=False,
    )


@pytest.mark.django_db
class TestAccountsAPI:
    def test_registration(self, api_client):
        url = reverse("accounts:registration")
        data = {
            "email": "newuser@test.com",
            "password": "StrongPassword123!",
            "password1": "StrongPassword123!",
        }
        response = api_client.post(url, data)
        assert response.status_code == 201
        user = User.objects.get(email="newuser@test.com")
        assert user.is_verified is False
        assert user.username

    def test_registration_password_mismatch(self, api_client):
        url = reverse("accounts:registration")
        data = {
            "email": "newuser@test.com",
            "password": "StrongPassword123!",
            "password1": "DifferentPassword123!",
        }
        response = api_client.post(url, data)
        assert response.status_code == 400

    def test_login_jwt_verified(self, api_client, verified_user):
        url = reverse("accounts:jwt-create")
        response = api_client.post(
            url,
            {"email": "test@test.com", "password": "StrongPassword123!"},
        )
        assert response.status_code == 200
        assert "access" in response.data

    def test_login_jwt_unverified_blocked(self, api_client, unverified_user):
        url = reverse("accounts:jwt-create")
        response = api_client.post(
            url,
            {"email": "unverified@test.com", "password": "StrongPassword123!"},
        )
        assert response.status_code == 400

    def test_login_token(self, api_client, verified_user):
        url = reverse("accounts:token-login")
        response = api_client.post(
            url,
            {"email": "test@test.com", "password": "StrongPassword123!"},
        )
        assert response.status_code == 200
        assert "token" in response.data

    def test_activation_flow(self, api_client, unverified_user):
        uid = urlsafe_base64_encode(force_bytes(unverified_user.pk))
        token = account_activation_token.make_token(unverified_user)
        url = reverse("accounts:activation", kwargs={"uidb64": uid, "token": token})
        response = api_client.get(url)
        assert response.status_code == 200
        unverified_user.refresh_from_db()
        assert unverified_user.is_verified is True

    def test_activation_post(self, api_client, unverified_user):
        uid = urlsafe_base64_encode(force_bytes(unverified_user.pk))
        token = account_activation_token.make_token(unverified_user)
        url = reverse("accounts:activation-post")
        response = api_client.post(url, {"uid": uid, "token": token})
        assert response.status_code == 200
        unverified_user.refresh_from_db()
        assert unverified_user.is_verified is True

    def test_activation_resend_no_enumeration(self, api_client):
        url = reverse("accounts:activation-resend")
        unknown = api_client.post(url, {"email": "nobody@test.com"})
        known = api_client.post(url, {"email": "test@test.com"})
        assert unknown.status_code == 200
        assert unknown.data == known.data

    def test_change_password(self, api_client, verified_user):
        api_client.force_authenticate(user=verified_user)
        url = reverse("accounts:change-password")
        response = api_client.put(
            url,
            {
                "old_password": "StrongPassword123!",
                "new_password": "NewStrongPassword456!",
                "new_password1": "NewStrongPassword456!",
            },
        )
        assert response.status_code == 200

    def test_profile_authenticated(self, api_client, verified_user):
        api_client.force_authenticate(user=verified_user)
        response = api_client.get(reverse("accounts:profile"))
        assert response.status_code == 200
        assert response.data["email"] == "test@test.com"

    def test_profile_unauthenticated(self, api_client):
        response = api_client.get(reverse("accounts:profile"))
        assert response.status_code == 401

    def test_password_reset_request_no_enumeration(self, api_client):
        url = reverse("accounts:password-reset")
        unknown = api_client.post(url, {"email": "missing@test.com"})
        assert unknown.status_code == 200
        assert unknown.data == PASSWORD_RESET_SENT_MESSAGE

    def test_password_reset_flow(self, api_client, verified_user):
        request_url = reverse("accounts:password-reset")
        api_client.post(request_url, {"email": "test@test.com"})

        uid = urlsafe_base64_encode(force_bytes(verified_user.pk))
        token = password_reset_token.make_token(verified_user)
        confirm_url = reverse("accounts:password-reset-confirm-post")
        response = api_client.post(
            confirm_url,
            {
                "uid": uid,
                "token": token,
                "new_password": "NewStrongPassword789!",
                "new_password1": "NewStrongPassword789!",
            },
        )
        assert response.status_code == 200
        verified_user.refresh_from_db()
        assert verified_user.check_password("NewStrongPassword789!")

    def test_activation_post_url_rejects_get(self, api_client):
        response = api_client.get(reverse("accounts:activation-post"))
        assert response.status_code == 405

    def test_password_reset_confirm_get(self, api_client, verified_user):
        uid = urlsafe_base64_encode(force_bytes(verified_user.pk))
        token = password_reset_token.make_token(verified_user)
        url = reverse(
            "accounts:password-reset-confirm",
            kwargs={"uidb64": uid, "token": token},
        )
        response = api_client.get(url)
        assert response.status_code == 200
        assert "confirm_url" in response.data
