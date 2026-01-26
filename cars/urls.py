from django.urls import path
from rest_framework.routers import DefaultRouter
from cars.views import CarView


router = DefaultRouter()
router.register("my-car", CarView, basename="my-car")

urlpatterns = router.urls