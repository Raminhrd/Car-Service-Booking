from django.db import models
from users.models import User

class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Car(models.Model):
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cars")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="cars")
    pelak = models.CharField(max_length=20, unique=True)

    vin = models.CharField(max_length=30, unique=True)
    model_year = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)


    def __str__(self):
        return f"{self.name} - {self.pelak}"
