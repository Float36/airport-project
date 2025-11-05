from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Extending the standard User admin
    to display and edit our 'role' field.
    """
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "role"
    )

    list_filter = UserAdmin.list_filter + ("role",)

    fieldsets = UserAdmin.fieldsets + (
        ("Custom Fields", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("role",)}),
    )
