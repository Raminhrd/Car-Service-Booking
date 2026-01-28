from django.contrib import admin
from booking.models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "car",
        "service",
        "start_at",
        "duration_minutes",
        "status",
        "created_at",
    )
    list_filter = ("status", "service", "created_at")
    search_fields = (
        "user__phone_number",
        "car__pelak",
        "car__vin",
        "service__title",
    )
    autocomplete_fields = ("user", "car", "service")
    ordering = ("-created_at",)
    date_hierarchy = "start_at"
    readonly_fields = ("created_at",)
