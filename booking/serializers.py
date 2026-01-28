from django.utils import timezone
from rest_framework import serializers

from booking.models import Booking


ACTIVE_STATUSES = {
    Booking.Status.PENDING,
    Booking.Status.CONFIRMED,
}


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Booking
        fields = (
            "id",
            "user",
            "car",
            "service",
            "start_at",
            "duration_minutes",
            "status",
            "note",
            "created_at",
        )
        read_only_fields = ("status", "created_at")

    def validate_start_at(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("start_at must be in the future.")
        return value

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user

        car = attrs.get("car")
        start_at = attrs.get("start_at")
        duration = attrs.get("duration_minutes")

        if car.owner_id != user.id:
            raise serializers.ValidationError({"car": "You can only book services for your own car."})

        service = attrs.get("service")
        if duration is None and service:
            attrs["duration_minutes"] = service.base_duration_minutes
            duration = attrs["duration_minutes"]

        end_at = start_at + timezone.timedelta(minutes=duration)

        qs = Booking.objects.filter(
            car=car,
            status__in=ACTIVE_STATUSES,
        )

        possible = qs.filter(start_at__lt=end_at).exclude(start_at__gte=end_at)

        for b in possible:
            b_end = b.start_at + timezone.timedelta(minutes=b.duration_minutes)
            if b.start_at < end_at and b_end > start_at:
                raise serializers.ValidationError("This car already has a booking in the selected time window.")

        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user

        if not validated_data.get("duration_minutes"):
            validated_data["duration_minutes"] = validated_data["service"].base_duration_minutes
        return super().create(validated_data)
