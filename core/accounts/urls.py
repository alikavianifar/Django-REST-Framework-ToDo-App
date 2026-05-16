from django.urls import include, path

from .views import signup

app_name = "accounts"

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("api/v1/", include("accounts.api.v1.urls")),
]
