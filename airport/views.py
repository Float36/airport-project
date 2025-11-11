from django.shortcuts import render
import logging
from django.http import Http404
from rest_framework import viewsets, permissions, serializers, exceptions
from .models import Country, City, Airline, Airplane, Airport, Flight, AirplaneType, Seat
from .filters import FlightFilter
from .serializers import (
    CountrySerializer,
    CitySerializer,
    CityCreateSerializer,

    AirportDetailSerializer,
    AirportListSerializer,
    AirportCreateSerializer,

    AirlineCreateSerializer,
    AirlineSerializer,

    AirplaneTypeSerializer,
    SeatSerializer,
    AirplaneSerializer,
    AirplaneCreateSerializer,

    FlightSerializer,
    FlightCreateSerializer
)


logger = logging.getLogger("airport")


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


class CountryViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CityViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = City.objects.select_related('country')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CitySerializer
        return CityCreateSerializer


class AirportViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = Airport.objects.select_related('city__country')

    def get_serializer_class(self):
        if self.action == 'list':
            return AirportListSerializer

        if self.action == 'retrieve':
            return AirportDetailSerializer

        return AirportCreateSerializer



class AirlineViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = Airline.objects.all()

    def get_serializer_class(self):
        if self.action in ['create']:
            return AirlineCreateSerializer
        return AirlineSerializer


class AirplaneTypeViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = [permissions.IsAdminUser]


class SeatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['airplane_type']


class AirplaneViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related('airline', 'airplane_type')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return AirplaneSerializer
        return AirplaneCreateSerializer


class FlightViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = Flight.objects.select_related(
        'departure_airport__city__country',
        'arrival_airport__city__country',
        'airplane__airline',
        'airplane__airplane_type'
    )

    filterset_class = FlightFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return FlightSerializer
        return FlightCreateSerializer



