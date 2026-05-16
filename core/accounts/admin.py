from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = (
        "email",
        "username",
        "is_superuser",
        "is_staff",
        "is_active",
        "is_verified",
    )
    list_filter = (
        "email",
        "is_superuser",
        "is_active",
    )
    search_fields = ("email",)
    ordering = ("email",)
    fieldsets = (
        (
            "Authentication",
            {
                "fields": ("email", "password"),
            },
        ),
        (
            "Permissions",
            {
                "fields": ("is_superuser", "is_staff", "is_active", "is_verified"),
            },
        ),
        (
            "Group Permissions",
            {
                "fields": (
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "Important date",
            {
                "fields": ("last_login",),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_superuser",
                    "is_staff",
                    "is_active",
                    "is_verified",
                ),
            },
        ),
    )


class CustomProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "first_name", "last_name", "created_date", "updated_date"]


admin.site.register(Profile, CustomProfileAdmin)
admin.site.register(User, CustomUserAdmin)
