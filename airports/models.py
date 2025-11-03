from django.db import models
from countries.models import Country


class Airports(models.Model):
    name = models.CharField(max_length=255)
    # unique code of airport
    iata_code = models.CharField(max_length=3, unique=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="airports")

    def __str__(self):
        return f"{self.name} ({self.iata_code}) - {self.country}"

