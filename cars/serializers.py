from rest_framework import serializers
from rest_framework.serializers import StringRelatedField
from rest_framework.serializers import ModelSerializer
from cars.models import Car, Category


class CarSerializer(ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)
    
    class Meta :
        model = Car
        fields = ("id", "name", "category", "owner", "pelak", "shomare_shasi", "model")