from django.shortcuts import render
from cars.models import Car, Category
from users.models import User
from cars.serializers import CarSerializer, CarCreateSerializer, CategorySerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.mixins import ListModelMixin, DestroyModelMixin, RetrieveModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class CarView(CreateModelMixin, ListModelMixin, DestroyModelMixin, RetrieveModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Car.objects.select_related("category").filter(owner=self.request.user)
    
    def get_serializer_class(self):
        if self.action == "create":
            return CarCreateSerializer
        return CarSerializer
    
    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)