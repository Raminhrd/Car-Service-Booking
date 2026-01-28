from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from cars.models import Car
from services.models import Service
from users.models import User

class Booking(models.Model):
    class Status(models.IntegerChoices):
        PENDING = 1, "Pending"
        CONFIRMED = 2, "Confirmed"
        CANCELED = 3, "Canceled"
        DONE = 4, "Done"
        NO_SHOW = 5, "No-show"

    user = models.ForeignKey(to=User,on_delete=models.CASCADE,related_name="bookings",)
    car = models.ForeignKey(Car,on_delete=models.CASCADE,related_name="bookings",)
    service = models.ForeignKey(Service,on_delete=models.PROTECT,related_name="bookings",)

    start_at = models.DateTimeField()
    duration_minutes = models.PositiveSmallIntegerField(default=30)

    status = models.IntegerField(choices=Status.choices, default=Status.PENDING)
    note = models.TextField(null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["car", "start_at"]),
            models.Index(fields=["user", "start_at"]),
        ]

    def __str__(self):
        return f"Booking#{self.id} - {self.user_id} - {self.service_id} @ {self.start_at}"
