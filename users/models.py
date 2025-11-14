from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", _("Admin")
        USER = "USER", _("User")

    role = models.CharField(max_length=5, choices=Role.choices, default=Role.USER)
