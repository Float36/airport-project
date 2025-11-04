from django.shortcuts import render
from rest_framework import viewsets
from .models import Country, Airline, Airplane, Airport, Flight
from .serializers import (
    CountrySerializer, AirportSerializer, AirlineSerializer,
    AirplaneSerializer, FlightSerializer, FlightCreateSerializer
)
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    # permission_classes = [IsAdminUser]

class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    # permission_classes = [IsAdminUser]

class AirlineViewSet(viewsets.ModelViewSet):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer
    # permission_classes = [IsAdminUser]

class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    # permission_classes = [IsAdminUser]

class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    # permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return FlightSerializer
        return FlightCreateSerializer



