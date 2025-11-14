import logging

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.mixins import AuditLoggingMixin

from .ai_services import get_ai_assistant
from .filters import FlightFilter
from .models import (
    Airline,
    Airplane,
    AirplaneType,
    Airport,
    City,
    Country,
    Flight,
    Seat,
)
from .serializers import (
    AirlineCreateSerializer,
    AirlineSerializer,
    AirplaneCreateSerializer,
    AirplaneSerializer,
    AirplaneTypeSerializer,
    AirportCreateSerializer,
    AirportDetailSerializer,
    AirportListSerializer,
    CityCreateSerializer,
    CitySerializer,
    CountrySerializer,
    FlightCreateSerializer,
    FlightSerializer,
    SeatSerializer,
)

logger = logging.getLogger("airport")


class CountryViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    logger = logger


class CityViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = City.objects.select_related("country")
    logger = logger

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return CitySerializer
        return CityCreateSerializer

    @action(detail=True, methods=["GET"], url_path="guide")
    def city_guide(self, request, pk=None):
        """
        GET /api/v1/cities/{id}/guide/
        Generate info about city
        """
        city = self.get_object()
        ai = get_ai_assistant()
        guide_text = ai.get_city_guide(city.name, city.country.name)

        return Response({"city": city.name, "ai_guide": guide_text})


class AirportViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = Airport.objects.select_related("city__country")
    logger = logger

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer

        if self.action == "retrieve":
            return AirportDetailSerializer

        return AirportCreateSerializer


class AirlineViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = Airline.objects.all()
    logger = logger

    def get_serializer_class(self):
        if self.action in ["create"]:
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
    filterset_fields = ["airplane_type"]
    logger = logger


class AirplaneViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airline", "airplane_type")
    logger = logger

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return AirplaneSerializer
        return AirplaneCreateSerializer


class FlightViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    queryset = Flight.objects.select_related(
        "departure_airport__city__country",
        "arrival_airport__city__country",
        "airplane__airline",
        "airplane__airplane_type",
    )

    filterset_class = FlightFilter

    logger = logger

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return FlightSerializer
        return FlightCreateSerializer
