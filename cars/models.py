from django.db import models 
from users.models import User

class Category(models.Model):
    name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Car(models.Model):
    name = models.CharField(max_length=30)
    owner = models.OneToOneField(to= User, on_delete=models.CASCADE)
    category = models.ForeignKey(to= Category, on_delete=models.CASCADE)
    pelak = models.CharField(max_length=8)
    shomare_shasi = models.PositiveIntegerField(max_length=10)
    model = models.DateField()

    def __str__(self):
        return self.name