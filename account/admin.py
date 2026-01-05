
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    # List page
    list_display = (
        "id",
        "email",
        "full_name",
        "role",
        "department",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )

    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
        "department",
    )

    search_fields = ("email", "full_name", "department")
    ordering = ("-date_joined",)

    # Detail page layout
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("full_name", "department")}),
        ("Role & Status", {"fields": ("role", "is_active", "is_staff")}),
        ("Permissions", {"fields": ("is_superuser", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    # Create user form
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "full_name",
                "department",
                "role",
                "password1",
                "password2",
                "is_active",
                "is_staff",
            ),
        }),
    )

    readonly_fields = ("date_joined", "last_login")

    filter_horizontal = ("groups", "user_permissions")

    USERNAME_FIELD = "email"