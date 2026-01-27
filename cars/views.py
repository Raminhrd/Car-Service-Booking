from django.shortcuts import render
from cars.models import Car
from users.models import User
from cars.serializers import CarSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin, DestroyModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet


class CarView(ListModelMixin, DestroyModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = CarSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Car.objects.select_related("category").filter(owner=self.request.user)