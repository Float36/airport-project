import logging

from rest_framework import viewsets

from core.mixins import AuditLoggingMixin

from .models import User
from .serializers import UserSerializer

logger = logging.getLogger("users")


class UserViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    """
    API for seen users
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    logger = logger
