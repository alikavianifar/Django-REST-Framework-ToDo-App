from django.contrib.auth.forms import UserCreationForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["email", "username", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user
