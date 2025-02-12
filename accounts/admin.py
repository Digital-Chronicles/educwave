from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.hashers import make_password
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "username", "is_staff", "is_active")

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get("password") and not obj.password.startswith("pbkdf2_sha256$"):
            obj.password = make_password(form.cleaned_data["password"])
        super().save_model(request, obj, form, change)

admin.site.register(CustomUser, CustomUserAdmin)
