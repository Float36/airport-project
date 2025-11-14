from rest_framework import serializers
from .models import Country, City, Airport, Airline, Airplane, Flight, AirplaneType, Seat


# --- Country ---
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'name')


class CitySerializer(serializers.ModelSerializer):
    """
    GET cities
    """
    country = CountrySerializer(read_only=True)

    class Meta:
        model = City
        fields = ('id', 'name', 'country')


class CityCreateSerializer(serializers.ModelSerializer):
    """
    POST/PUT cities
    """
    class Meta:
        model = City
        fields = ('name', 'country')




# --- Airport ---
class AirportListSerializer(serializers.ModelSerializer):
    """
    (GET) without iata_code
    """
    city = CitySerializer(read_only=True)

    class Meta:
        model = Airport
        fields = ('id', 'name', 'city')

class AirportDetailSerializer(serializers.ModelSerializer):
    # Show city object
    city = CitySerializer(read_only=True)

    class Meta:
        model = Airport
        fields = ('id', 'name', 'iata_code', 'city')


class AirportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ('name', 'iata_code', 'city')


# --- Airline ---
class AirlineSerializer(serializers.ModelSerializer):
    """
    Serializer for (GET) airlines
    """
    home_base = AirportDetailSerializer(read_only=True)

    class Meta:
        model = Airline
        fields = ('id', 'name', 'home_base')


class AirlineCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for (POST) airlines
    """
    class Meta:
        model = Airline
        fields = ('name', 'home_base')


class AirplaneTypeSerializer(serializers.ModelSerializer):
    """
    GET/POST for AirlineType
    """
    # Add from @property
    capacity =serializers.IntegerField(read_only=True)

    class Meta:
        model = AirplaneType
        fields = ('id', 'name', 'capacity')


class SeatSerializer(serializers.ModelSerializer):
    """
    GET serializer
    """
    seat_type = serializers.CharField(source="get_seat_type_display")

    class Meta:
        model = Seat
        fields = ('id', 'airplane_type', 'row', 'seat', 'seat_type')


class AirplaneSerializer(serializers.ModelSerializer):
    """
    Serializer for (GET) planes
    """
    # Show airline name
    airline = AirlineSerializer(read_only=True)
    airplane_type = AirplaneTypeSerializer(read_only=True)

    class Meta:
        model = Airplane
        fields = ('id', 'airline', 'airplane_type')


class AirplaneCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for (POST) planes
    """
    class Meta:
        model = Airplane
        fields = ('name', 'airline', 'airplane_type')



# Serializers for Flights
class FlightSerializer(serializers.ModelSerializer):
    """
    Serializer for GET all flights information
    """
    departure_airport = AirportDetailSerializer(read_only=True)
    arrival_airport = AirportDetailSerializer(read_only=True)
    airplane = AirplaneSerializer(read_only=True)
    status = serializers.CharField(source='get_status_display') # Show "Scheduled" instead of "SCHEDULED"

    class Meta:
        model = Flight
        fields = (
            'id',
            'flight_number',
            'departure_airport',
            'arrival_airport',
            'departure_time',
            'arrival_time',
            'airplane',
            'status',
            'price'
        )

class FlightCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for POST/PUT flights
    """
    class Meta:
        model = Flight
        fields = (
            'flight_number',
            'departure_airport',
            'arrival_airport',
            'departure_time',
            'arrival_time',
            'airplane',
            'status',
            'price'
        )
