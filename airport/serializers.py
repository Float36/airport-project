from rest_framework import serializers
from .models import Country, City, Airport, Airline, Airplane, Flight


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


class AirplaneSerializer(serializers.ModelSerializer):
    """
    Serializer for (GET) planes
    """
    # Show airline name
    airline = AirlineSerializer(read_only=True)

    class Meta:
        model = Airplane
        fields = ('id', 'model', 'capacity', 'airline')

class AirplaneCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for (POST) planes
    """
    class Meta:
        model = Airplane
        fields = ('model', 'capacity', 'airline')



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
            'status'
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
            'status'
        )
