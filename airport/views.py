from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Country, City, Airline, Airplane, Airport, Flight, AirplaneType, Seat
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


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.select_related('country')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CitySerializer
        return CityCreateSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.select_related('city__country')

    def get_serializer_class(self):
        if self.action == 'list':
            return AirportListSerializer

        if self.action == 'retrieve':
            return AirportDetailSerializer

        return AirportCreateSerializer



class AirlineViewSet(viewsets.ModelViewSet):
    queryset = Airline.objects.all()

    def get_serializer_class(self):
        if self.action in ['create']:
            return AirlineCreateSerializer
        return AirlineSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = [permissions.IsAdminUser]


class SeatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['airplane_type']


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related('airline', 'airplane_type')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return AirplaneSerializer
        return AirplaneCreateSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.select_related(
        'departure_airport__city__country',
        'arrival_airport__city__country',
        'airplane__airline',
        'airplane__airplane_type'
    )

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return FlightSerializer
        return FlightCreateSerializer



