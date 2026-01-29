from rest_framework.routers import DefaultRouter
from booking.views import BookingViewSet

router = DefaultRouter()
router.register("booking", BookingViewSet, basename="booking")

urlpatterns = router.urls