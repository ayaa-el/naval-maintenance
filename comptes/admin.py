from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Rôle (RBAC)", {"fields": ("role",)}),
    )
    list_display = ("username", "role", "is_active")
    list_filter = ("role", "is_active")