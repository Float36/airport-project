from rest_framework import serializers
from .models import Ticket
from airport.serializers import FlightSerializer
from users.serializers import UserSerializer


class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer for (GET) tickets
    """
    flight = FlightSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Ticket
        fields = ('id', 'user', 'flight', 'seat', 'status', 'created_at')


class TicketCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for (POST) tickets
    """
    class Meta:
        model = Ticket
        fields = ('flight', 'seat')

    def validate(self, data):
        flight = data['flight']
        seat = data['seat']

        if Ticket.objects.filter(flight=flight, seat=seat).exists():
            raise serializers.ValidationError(
                f"Seat {seat} is already booked for flight {flight.flight_number}"
            )

        if seat > flight.airplane.capacity:
            raise serializers.ValidationError(
                f"Seat {seat} doesn't exist on this plane (capacity: {flight.airplane.capacity}"
            )

        return data



