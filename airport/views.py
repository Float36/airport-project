from django.shortcuts import render
from rest_framework import viewsets
from .models import Country, Airline, Airplane, Airport, Flight
from .serializers import (
    CountrySerializer, AirportSerializer, AirportCreateSerializer, AirlineSerializer,
    AirplaneSerializer, AirplaneCreateSerializer, FlightSerializer, FlightCreateSerializer
)


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.select_related('country')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return AirportSerializer
        return AirportCreateSerializer



class AirlineViewSet(viewsets.ModelViewSet):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related('airline')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return AirplaneSerializer
        return AirplaneCreateSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.select_related(
        'departure_airport__country',
        'arrival_airport__country',
        'airplane__airline'
    )

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return FlightSerializer
        return FlightCreateSerializer



