from rest_framework.routers import DefaultRouter
from booking.views import BookingViewSet

router = DefaultRouter()
router.register("book", BookingViewSet, basename="book")

urlpatterns = router.urls