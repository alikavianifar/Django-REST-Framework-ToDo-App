from django.contrib.auth.backends import ModelBackend


class VerifiedEmailBackend(ModelBackend):
    """Web login: require verified email unless superuser."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(
            request, username=username, password=password, **kwargs
        )
        if user is None:
            return None
        if user.is_superuser:
            return user
        if not user.is_verified:
            return None
        return user
