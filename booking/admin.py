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