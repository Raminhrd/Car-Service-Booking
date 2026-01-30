from datetime import datetime, time, timedelta
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from booking.serializers import BookingSerializer

from booking.models import Booking


class BookingViewSet(ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.select_related("car", "service").filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated], url_path="available")
    def available(self, request):
        service_id = request.query_params.get("service_id")
        date_str = request.query_params.get("date")

        if not service_id or not date_str:
            return Response({"error": "service_id and date are required"}, status=400)

        day = datetime.fromisoformat(date_str).date()
        start_day = timezone.make_aware(datetime.combine(day, time(9, 0)))
        end_day = timezone.make_aware(datetime.combine(day, time(18, 0)))

        slot_minutes = 30 
        slots = []
        cur = start_day
        while cur + timedelta(minutes=slot_minutes) <= end_day:
            slots.append(cur)
            cur += timedelta(minutes=slot_minutes)

        active = Booking.objects.filter(
            status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED],
            start_at__lt=end_day,
            start_at__gte=start_day,
        ).only("start_at", "duration_minutes")

        busy = []
        for b in active:
            busy.append((b.start_at, b.start_at + timedelta(minutes=b.duration_minutes)))

        free = []
        for s in slots:
            e = s + timedelta(minutes=slot_minutes)
            overlap = any(bs < e and be > s for bs, be in busy)
            if not overlap:
                free.append(s.isoformat())

        return Response({"date": date_str, "free_slots": free})
