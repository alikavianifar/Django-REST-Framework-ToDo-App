from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from accounts.tasks import send_email_task
from accounts.tokens import account_activation_token, password_reset_token

ACTIVATION_SENT_MESSAGE = {
    "detail": "If an account exists with this email, an activation link has been sent."
}

PASSWORD_RESET_SENT_MESSAGE = {
    "detail": "If an account exists with this email, a password reset link has been sent."
}


def build_activation_link(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    return f"{settings.SITE_URL}/api/v1/activation/confirm/{uid}/{token}/"


def build_password_reset_link(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = password_reset_token.make_token(user)
    return f"{settings.SITE_URL}/api/v1/password/reset/confirm/{uid}/{token}/"


def send_activation_email(user):
    send_email_task.delay(
        "email/activation_email.tpl",
        {
            "activation_link": build_activation_link(user),
            "site_url": settings.SITE_URL,
        },
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )


def send_password_reset_email(user):
    send_email_task.delay(
        "email/password_reset_email.tpl",
        {
            "reset_link": build_password_reset_link(user),
            "site_url": settings.SITE_URL,
            "confirm_api_url": f"{settings.SITE_URL}/api/v1/password/reset/confirm/",
        },
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )
