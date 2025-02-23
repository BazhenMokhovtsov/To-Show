from django.contrib import admin

from .models.profile import Profile
from .models.user import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "email"]
    list_per_page = 20
    search_fields = ["username", "email"]
    list_filter = ["is_staff", "is_active"]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "settings"]
    list_per_page = 20
    search_fields = ["user__username", "user__email"]
    list_filter = ["user__is_staff", "user__is_active"]
