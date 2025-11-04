from rest_framework import serializers
from .models import Country, Airport, Airline, Airplane, Flight

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'name')

class AirportSerializer(serializers.ModelSerializer):
    # Show country name
    country = serializers.StringRelatedField()

    class Meta:
        model = Airport
        fields = ('id', 'name', 'iata_code', 'country')


class AirlineSerializer(serializers.ModelSerializer):
    home_base = serializers.StringRelatedField()

    class Meta:
        model = Airline
        fields = ('id', 'name', 'home_base')


class AirplaneSerializer(serializers.ModelSerializer):
    # Show airline name
    airline = serializers.StringRelatedField()

    class Meta:
        model = Airplane
        fields = ('id', 'model', 'capacity', 'airline')



# Serializers for Flights
class FlightSerializer(serializers.ModelSerializer):
    """
    Serializer for GET all flights information
    """
    departure_airport = AirportSerializer(read_only=True)
    arrival_airport = AirportSerializer(read_only=True)
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
            'arriving_time',
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
            'arriving_time',
            'airplane',
            'status'
        )
