from django.db import models
from django.utils.translation import gettext_lazy as _

class Country(models.Model):
    """
    Country class
    """
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name


class Airport(models.Model):
    """
    Airports class
    """
    name = models.CharField(max_length=255)
    # Unique code of airport
    iata_code = models.CharField(max_length=3, unique=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="airports")

    def __str__(self):
        return f"{self.name} ({self.iata_code}) - {self.country.name}"


class Airline(models.Model):
    """
    Airlines company class
    """
    name = models.CharField(max_length=255, unique=True)
    # FK on airport, 1 airport can have alot airlines
    home_base = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="airlines"
    )

    def __str__(self):
        return self.name


class Airplane(models.Model):
    model = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="airplanes")

    def __str__(self):
        return f"{self.model} ({self.capacity})"


class Flight(models.Model):
    """
    Flight class
    """
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", _("Scheduled")
        BOARDING = "BOARDING", _("Boarding")
        DEPARTED = "DEPARTED", _("Departed")
        DELAYED = "DELAYED", _("Delayed")
        CANCELLED = "CANCELLED", _("Cancelled")

    flight_number = models.CharField(max_length=10, unique=True)
    departure_airport = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name='departing_flights'
    )
    arrival_airport = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="arriving_flights"
    )
    departure_time = models.DateTimeField()
    arriving_time = models.DateTimeField()
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.SCHEDULED
    )

    class Meta:
        ordering = ['departure_time']

    def __str__(self):
        return f"{self.flight_number}: {self.departure_airport} to {self.arrival_airport}"






