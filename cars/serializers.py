from rest_framework import serializers
from cars.models import Car, Category


class CarCreateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.filter(is_active=True))

    class Meta:
        model = Car
        fields = ("id", "name", "category", "pelak", "vin", "model_year")
        read_only_fields = ("id",)


class CarSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Car
        fields = ("id", "name", "category", "owner", "pelak", "vin", "model_year", "created_at")