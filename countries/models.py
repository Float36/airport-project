from django.contrib.admin.utils import unquote
from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    class Meta:
        ordering = ['name']
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name

