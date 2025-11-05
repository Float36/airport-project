from rest_framework import serializers
from .models import Ticket, Order
from airport.models import Flight
from airport.serializers import FlightSerializer


class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer for (GET) tickets
    """
    flight = FlightSerializer(read_only=True)
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Ticket
        fields = (
            'id', 'flight', 'passenger_first_name',
            'passenger_last_name', 'seat', 'status',
        )


class TicketCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for (POST) tickets
    """
    class Meta:
        model = Ticket
        fields = (
            'flight',
            'passenger_first_name',
            'passenger_last_name',
            'seat',
            'status',
        )

    def validate(self, data):
        flight = data['flight']
        seat = data['seat']

        # Is a seat able for booking
        if Ticket.objects.filter(flight=flight, seat=seat).exists():
            raise serializers.ValidationError(
                f"Seat {seat} is already booked for flight {flight.flight_number}"
            )

        # Seat exist on plane
        if seat > flight.airplane.capacity:
            raise serializers.ValidationError(
                f"Seat {seat} doesn't exist on this plane (capacity: {flight.airplane.capacity}"
            )

        return data



class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for (GET) orders
    """
    tickets = TicketSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField()
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Order
        fields = ('id', 'user', 'created_at', 'status', 'tickets')


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for (POST) orders
    """
    tickets = TicketCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ("tickets",)


    def validate_tickets(self, tickets_data):
        # Is list not empty
        if not tickets_data:
            raise serializers.ValidationError("Order must contain at least one ticket.")

        # Check for duplicate seats in one order
        seats_on_flight = set()
        for ticket_data in tickets_data:
            flight_seat = (ticket_data['flight'].id, ticket_data['seat'])
            if flight_seat in seats_on_flight:
                raise serializers.ValidationError(
                    f"Duplicate ticket for seat {ticket_data['seat']} "
                    f"on flight {ticket_data['flight'].flight_number} "
                    "in the same order."
                )
            seats_on_flight.add(flight_seat)

        return tickets_data

    # We override .create() to handle nested tickets.
    def create(self, validate_data):
        tickets_data = validate_data.pop('tickets')
        order = Order.objects.create(**validate_data)

        for ticket_data in tickets_data:
            Ticket.objects.create(order=order, **ticket_data)

        return order

