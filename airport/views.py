from django.shortcuts import render
import logging
from django.http import Http404
from rest_framework import viewsets, permissions, serializers, exceptions
from .models import Country, City, Airline, Airplane, Airport, Flight, AirplaneType, Seat
from .filters import FlightFilter
from core.mixins import AuditLoggingMixin
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


class CountryViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    logger = logger


class CityViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = City.objects.select_related('country')
    logger = logger

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CitySerializer
        return CityCreateSerializer


class AirportViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = Airport.objects.select_related('city__country')
    logger = logger

    def get_serializer_class(self):
        if self.action == 'list':
            return AirportListSerializer

        if self.action == 'retrieve':
            return AirportDetailSerializer

        return AirportCreateSerializer



class AirlineViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = Airline.objects.all()
    logger = logger

    def get_serializer_class(self):
        if self.action in ['create']:
            return AirlineCreateSerializer
        return AirlineSerializer


class AirplaneTypeViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = [permissions.IsAdminUser]
    logger = logger


class SeatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['airplane_type']
    logger = logger


class AirplaneViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related('airline', 'airplane_type')
    logger = logger

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

    logger = logger

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return FlightSerializer
        return FlightCreateSerializer



