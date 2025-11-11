from django.db import transaction
from rest_framework import serializers
from .models import Ticket, Order, Transaction
from airport.models import Flight, Seat
from airport.serializers import FlightSerializer, SeatSerializer
import logging


logger = logging.getLogger("booking")


class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer for (GET) tickets
    """
    flight = FlightSerializer(read_only=True)
    seat = SeatSerializer(read_only=True)
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
    # 'seat' is waiting for ID
    seat = serializers.PrimaryKeyRelatedField(
        queryset=Seat.objects.all()
    )

    flight = serializers.PrimaryKeyRelatedField(
        queryset=Flight.objects.all()
    )
    class Meta:
        model = Ticket
        fields = (
            'flight',
            'passenger_first_name',
            'passenger_last_name',
            'seat',
        )

    def validate(self, data):
        flight = data['flight']
        seat = data['seat']

        # Check if the "drawing" of the seat matches the "drawing" of the plane
        if seat.airplane_type != flight.airplane.airplane_type:
            logger.warning(
                "Ticket validation failed: Seat type mismatch. "
                f"Flight {flight.id} (AirplaneType: {flight.airplane.airplane_type.name}) "
                f"vs Seat {seat.id} (AirplaneType: {seat.airplane_type.name})."
            )
            raise serializers.ValidationError(
                f"Seat {seat} ({seat.airplane_type.name}) "
                f"is not valid for this flight's airplane "
                f"({flight.airplane.airplane_type.name})."
            )

        return data


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for transaction
    """
    status = serializers.CharField(source="get_status_display")

    class Meta:
        model = Transaction
        fields = (
            'id',
            'status',
            'amount',
            'currency',
            'provider_transaction_id',
            'created_at',
        )


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for (GET) orders
    """
    tickets = TicketSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField()
    status = serializers.CharField(source='get_status_display')
    transactions = TransactionSerializer(many=True, read_only=True)


    class Meta:
        model = Order
        fields = ('id', 'user', 'created_at', 'status', 'tickets', 'transactions')


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
            logger.warning(
                "Order validation failed: "
                "Attempted to create an order with an empty ticket list."
            )
            raise serializers.ValidationError("Order must contain at least one ticket.")

        # Check for duplicate seats in one order
        seats_on_flight = set()
        for ticket_data in tickets_data:
            flight_seat = (ticket_data['flight'].id, ticket_data['seat'].id)
            if flight_seat in seats_on_flight:
                logger.warning(
                    "Order validation failed: Duplicate ticket in the same order. "
                    f"Flight: {ticket_data['flight'].id}, Seat: {ticket_data['seat'].id}"
                )

                raise serializers.ValidationError(
                    f"Duplicate ticket for seat {ticket_data['seat']} "
                    f"on flight {ticket_data['flight'].flight_number} "
                    "in the same order."
                )
            seats_on_flight.add(flight_seat)

        return tickets_data

    # create() to handle nested tickets
    def create(self, validated_data):
        tickets_data = validated_data.pop('tickets')
        try:
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)

        except Exception as e:
            user_id = validated_data.get('user', 'unknown_user').id
            logger.error(
                f"Atomic creation of Order failed for user {user_id}. Error: {e}",
                exc_info=True
            )
            raise serializers.ValidationError(f"Could not create order: {e}")

        return order

