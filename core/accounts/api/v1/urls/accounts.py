from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .. import views

urlpatterns = [
    path("registration/", views.RegistrationApiView.as_view(), name="registration"),
    path(
        "change/password/",
        views.ChangePasswordApiView.as_view(),
        name="change-password",
    ),
    path(
        "activation/confirm/<str:uidb64>/<str:token>/",
        views.ActivationApiView.as_view(),
        name="activation",
    ),
    path(
        "activation/confirm/",
        views.ActivationApiView.as_view(),
        name="activation-post",
    ),
    path(
        "activation/resend/",
        views.ActivationResendApiView.as_view(),
        name="activation-resend",
    ),
    path("token/login/", views.CustomAuthToken.as_view(), name="token-login"),
    path("token/logout/", views.CustomDiscardAuthToken.as_view(), name="token-logout"),
    path("jwt/create/", views.CustomTokenObtainPairView.as_view(), name="jwt-create"),
    path(
        "jwt/refresh/",
        TokenRefreshView.as_view(permission_classes=[AllowAny]),
        name="jwt-refresh",
    ),
    path(
        "jwt/verify/",
        TokenVerifyView.as_view(permission_classes=[AllowAny]),
        name="jwt-verify",
    ),
    path("jwt/logout/", views.CustomTokenBlacklistView.as_view(), name="jwt-logout"),
    path(
        "password/reset/",
        views.PasswordResetRequestApiView.as_view(),
        name="password-reset",
    ),
    path(
        "password/reset/confirm/<str:uidb64>/<str:token>/",
        views.PasswordResetConfirmApiView.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "password/reset/confirm/",
        views.PasswordResetConfirmApiView.as_view(),
        name="password-reset-confirm-post",
    ),
]
