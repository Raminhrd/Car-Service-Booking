from django.shortcuts import render
from cars.models import Car
from users.models import User
from cars.serializers import CarSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin, DestroyModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet


class CarView(ListModelMixin, DestroyModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Car.objects.select_related("owner").all()
    serializer_class = CarSerializer
    permission_classes = [IsAuthenticated]