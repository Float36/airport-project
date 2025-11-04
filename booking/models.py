from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from airport.models import Flight

class Ticket(models.Model):
    class Status(models.TextChoices):
        BOOKED = "BOOKED", _("Booked")
        CANCELLED = "CANCELLED", _("Cancelled")
        USED = "USED", _("Used")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    seat = models.PositiveIntegerField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.BOOKED
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('flight', 'seat')
        ordering = ["-created_at"]

    def __str__(self):
        return f"Ticket for {self.user} on flight {self.flight.flight_number} (Seat: {self.seat})"