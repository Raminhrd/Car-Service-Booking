from django.contrib import admin
from services.models import Service

admin.register(Service)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id",
            "title",
            "service_type",
            "service_type_display",
            "description",
            "base_duration_minutes")