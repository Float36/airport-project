from django.shortcuts import render
import logging
from django.http import Http404
from rest_framework import viewsets, serializers, exceptions
from .models import User
from .serializers import UserSerializer


logger = logging.getLogger("users")


class AuditLoggingMixin:
    """
    Mixin for automatic logging CRUD
    """
    def get_user_str(self):
        """Get 'User: 1' or 'AnonymousUser'"""
        user = self.request.user
        if user and user.is_authenticated:
            return f"User {user.id} ({user.username})"
        return "AnonymousUser"

    def perform_create(self, serializer):
        super().perform_create(serializer)
        instance = serializer.instance
        logger.info(
            f"{self.get_user_str()} CREATED {instance.__class__.__name__} "
            f"(ID: {instance.id})"
        )

    def perform_update(self, serializer):
        super().perform_update(serializer)
        instance = serializer.instance
        logger.info(
            f"{self.get_user_str()} UPDATED {instance.__class__.__name__} "
            f"(ID: {instance.id})"
        )

    def perform_destroy(self, instance):
        obj_id = instance.id
        obj_class_name = instance.__class__.__name__

        super().perform_destroy(instance)

        logger.info(
            f"{self.get_user_str()} DELETED {obj_class_name} "
            f"(ID: {obj_id})"
        )

    def handle_exception(self, exc):
        """
        Logging for exception
        """
        response = super().handle_exception(exc)

        user_str = self.get_user_str()
        view_name = self.__class__.__name__
        action = self.action

        if isinstance(exc, serializers.ValidationError):
            # Err 400
            logger.warning(
                f"{user_str} Validation Failed (400) on {action} "
                f"in {view_name}: {exc.detail}"
            )

        elif isinstance(exc, (exceptions.PermissionDenied, exceptions.NotAuthenticated)):
            # Err 403/401
            logger.warning(
                f"{user_str} Access Denied (401/403) on {action} "
                f"in {view_name}: {exc.detail}"
            )

        elif isinstance(exc, Http404):
            # Err 404
            logger.warning(
                f"{user_str} Not Found (404) on {action} "
                f"in {view_name}: {exc.detail}"
            )

        else:
            # Other (500)
            logger.error(
                f"{user_str} Unhandled Server Error (500) on {action} "
                f"in {view_name}: {exc}",
                exc_info=True
            )

        return response


class UserViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    """
    API for seen users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer