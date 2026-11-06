from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CastleForeverUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Contact", {"fields": ("phone",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Contact", {"fields": ("email", "phone")}),)
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
