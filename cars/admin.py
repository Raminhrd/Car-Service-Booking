from django.contrib import admin
from cars.models import Car, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id","name", "is_active")


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("id", "name","owner", "category", "pelak", "vin")