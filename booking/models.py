from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from airport.models import Flight, Seat


class Order(models.Model):
    """
    Model order is a container for tickets
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")  # awaiting payment
        PAID = "PAID", _("Paid")
        CANCELLED = "CANCELLED", _("Cancelled")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Order #{self.id} by {self.user.username} "
            f"({self.get_status_display()})"
        )


class Ticket(models.Model):
    class Status(models.TextChoices):
        BOOKED = "BOOKED", _("Booked")
        CONFIRMED = "CONFIRMED", _("Confirmed")
        CANCELLED = "CANCELLED", _("Cancelled")
        USED = "USED", _("Used")

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    passenger_first_name = models.CharField(max_length=255)
    passenger_last_name = models.CharField(max_length=255)

    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name="tickets")

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.BOOKED
    )

    class Meta:
        unique_together = ("flight", "seat")
        ordering = ["passenger_last_name", "passenger_first_name"]

    def __str__(self):
        return (
            f"{self.passenger_first_name} {self.passenger_last_name} "
            f"(Flight: {self.flight.flight_number}, Seat: {self.seat.row}{self.seat.seat})"
        )


class Transaction(models.Model):
    """
    Model for storing payment transactions
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")  # Payment initiated
        SUCCESS = "SUCCESS", _("Success")  # Payment successful
        FAILED = "FAILED", _("Failed")  # Payment failed

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="transaction"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=5, default="USD")
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )

    provider_transaction_id = models.CharField(
        max_length=255, blank=True, null=True, db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Transaction #{self.id} for Order #{self.order.id} "
            f"({self.get_status_display()}) - {self.amount} {self.currency}"
        )
