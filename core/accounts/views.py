from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.forms import CustomUserCreationForm
from accounts.utils import send_activation_email


def signup(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_verified = False
            user.save()
            send_activation_email(user)
            messages.success(
                request,
                "Account created. Please check your email to activate before signing in.",
            )
            return redirect("accounts:login")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})
