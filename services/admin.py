from django.contrib import admin
from services.models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "service_type",
        "get_service_type_display",
        "base_duration_minutes",
        "is_active",
    )

    list_filter = ("service_type", "is_active")
    search_fields = ("title",)
