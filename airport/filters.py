import django_filters
from .models import Flight


class FlightFilter(django_filters.FilterSet):
    # Filter on city name
    departure_city = django_filters.CharFilter(
        field_name="departure_airport__city__name",
        lookup_expr="icontains"
    )

    arrival_city = django_filters.CharFilter(
        field_name="arrival_airport__city__name",
        lookup_expr="icontains"
    )

    class Meta:
        model = Flight
        fields = {
            "status": ["exact"],                    # ?status=SCHEDULED
            "departure_time": ["gte", "lte"],       # ?departure_time__gte=
        }
