from django.db import models
from django.utils.translation import gettext_lazy as _


class Service(models.Model):
    class Type(models.IntegerChoices):

        Periodic = 1, _("Periodic")
        Mechanical = 2, _("Mechanical")
        Body = 3, _("Body/Paint")
        Detailing = 4, _("Detailing")

    title = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    base_duration_minutes = models.PositiveSmallIntegerField(default=30)
    service_type = models.IntegerField(choices=Type.choices)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title