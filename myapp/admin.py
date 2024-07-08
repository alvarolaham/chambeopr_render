from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MyUser, PasswordResetCode


class CustomUserAdmin(UserAdmin):
    list_display = ("email", "username", "first_name", "last_name", "is_admin")
    list_filter = ("is_admin", "is_active")  # Changed from 'is_staff' to 'is_admin'
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("username", "first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_admin",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
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
                    "username",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


admin.site.register(MyUser, CustomUserAdmin)
admin.site.register(PasswordResetCode)
