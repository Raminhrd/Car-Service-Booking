from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from booking.models import Booking
from booking.serializers import BookingSerializer


class BookingViewSet(ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.select_related("car", "service").filter(user=self.request.user)
