from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class VerifiedUserRequiredMixin(LoginRequiredMixin):
    """Require login and a verified email for template views."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_verified:
            messages.warning(
                request,
                "Please verify your email before using the application.",
            )
            return redirect("accounts:login")
        return super().dispatch(request, *args, **kwargs)
