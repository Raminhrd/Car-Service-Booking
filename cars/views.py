from django.shortcuts import render
from cars.models import Car
from users.models import User
from cars.serializers import CarSerializer, CarCreateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin, DestroyModelMixin, RetrieveModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet


class CarView(CreateModelMixin, ListModelMixin, DestroyModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = CarSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Car.objects.select_related("category").filter(owner=self.request.user)
    
    def get_serializer_class(self):
        if self.action == ["create"]:
            return CarCreateSerializer
        return CarSerializer
    
    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)