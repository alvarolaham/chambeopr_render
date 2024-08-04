from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import MyUser, PasswordResetCode, ProAccount, Service, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_superuser",
        "is_pro",
    )
    list_filter = ("is_superuser", "is_active", "is_pro")
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
                    "is_superuser",
                    "is_pro",
                    "pro_account_created_at",
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
                    "is_superuser",
                    "is_pro",
                ),
            },
        ),
    )


class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "created_at", "updated_at")
    list_filter = ("category",)
    search_fields = ("name", "category")


class ProAccountAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "business_name",
        "phone_number",
        "zip_code",
        "created_at",
    )
    search_fields = (
        "user__username",
        "user__email",
        "business_name",
        "phone_number",
        "zip_code",
    )
    filter_horizontal = ("services",)


admin.site.register(MyUser, CustomUserAdmin)
admin.site.register(PasswordResetCode)
admin.site.register(Service, ServiceAdmin)
admin.site.register(ProAccount, ProAccountAdmin)
admin.site.register(UserProfile)
