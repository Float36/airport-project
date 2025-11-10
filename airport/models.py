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


class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="cities"
    )

    class Meta:
        unique_together = ('name', 'country')
        ordering = ["name"]
        verbose_name_plural = "cities"

    def __str__(self):
        return f"{self.name} ({self.country})"



class Airport(models.Model):
    """
    Airports class
    """
    name = models.CharField(max_length=255)
    # Unique code of airport
    iata_code = models.CharField(max_length=3, unique=True)
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="airports"
    )

    def __str__(self):
        return f"{self.name} ({self.iata_code}) - {self.city.name}, {self.city.country.name}"

class Airline(models.Model):
    """
    Airlines company class
    """
    name = models.CharField(max_length=255, unique=True)
    # FK on airport, 1 airport can have alot airlines
    home_base = models.ForeignKey(
        Airport,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="airlines"
    )

    def __str__(self):
        return self.name


class AirplaneType(models.Model):
    """
    New model for type of airplane
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    @property
    def capacity(self):
        """Dynamic capacity count"""
        return self.seats.count()


class Seat(models.Model):
    """
    Describes a specific seat on an airplane
    """
    class SeatType(models.TextChoices):
        ECONOMY = "ECONOMY", _("Economy")
        BUSINESS = "BUSINESS", _("Business")
        FIRST = "FIRST", _("First")

    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="seats"
    )
    row = models.PositiveIntegerField()     # row: 1, 2, 3
    seat = models.CharField(max_length=1)   # seat: A, B, C
    seat_type = models.CharField(
        max_length=10,
        choices=SeatType.choices,
        default=SeatType.ECONOMY
    )

    class Meta:
        unique_together = ('airplane_type', 'row', 'seat')
        ordering = ['row', 'seat']

    def __str__(self):
        return f"{self.airplane_type.name}: {self.row}{self.seat} ({self.get_seat_type_display()})"


class Airplane(models.Model):
    """
    Airplane with a unique number
    """
    name = models.CharField(max_length=100)   # aircraft number(name) ex: UR-PSR
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes"
    )
    airline = models.ForeignKey(
        Airline,
        on_delete=models.CASCADE,
        related_name="airplanes"
    )

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
    arrival_time = models.DateTimeField()
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

    @property
    def available_seats_count(self):
        """
        Dynamic seats count
        """
        total_capacity = self.airplane.airplane_type.capacity
        booked_tickets = self.tickets.count()
        return total_capacity - booked_tickets






