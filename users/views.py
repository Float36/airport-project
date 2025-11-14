import logging
from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer
from core.mixins import AuditLoggingMixin


logger = logging.getLogger("users")


class UserViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    """
    API for seen users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    logger = logger