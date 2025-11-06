from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .models import Ticket, Order
from .serializers import (
    TicketSerializer, TicketCreateSerializer,
    OrderSerializer, OrderCreateSerializer
)


class OrderViewSet(
    mixins.CreateModelMixin,        # POST
    mixins.ListModelMixin,          # GET
    mixins.RetrieveModelMixin,      # GET /id/
    viewsets.GenericViewSet
):
    """
    ViewSet for Creating and Viewing Orders.
    - Creates a new order (with tickets).
    - User sees ONLY THEIR orders.
    - Admin sees ALL orders.
    """
    def get_queryset(self):
        """
        Filter:
        - User sees ONLY THEIR orders.
        - Admin sees ALL orders.
        """
        user = self.request.user
        base_queryset = Order.objects.prefetch_related(
            'tickets__seat',
            'tickets__flight__departure_airport',
            'tickets__flight__arrival_airport',
            'tickets__flight__airplane__airplane_type'
        )

        if user.is_staff or (hasattr(user, 'role') and user.role == 'ADMIN'):
            return base_queryset.all()

        return base_queryset.filter(user=user)

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """
        Automatically bind the order to the current
        user and set the status to PENDING.
        """
        serializer.save(
            user=self.request.user,
            status=Order.Status.PENDING
        )


class TicketViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    (For Admins) Read-Only ViewSet to view ALL tickets in the system
    """
    queryset = Ticket.objects.select_related(
        'order__user',
        'seat',
        'flight__departure_airport',
        'flight__arrival_airport',
        'flight__airplane__airplane_type'
    )
    serializer_class = TicketSerializer
    permission_classes = [IsAdminUser]
