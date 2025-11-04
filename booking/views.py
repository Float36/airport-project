from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .models import Ticket
from .serializers import TicketSerializer, TicketCreateSerializer


class TicketViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        """
        Filter tickets:
        - admin see all
        - user see his
        """
        user = self.request.user
        if user.is_staff or user.role == "ADMIN":
            return Ticket.objects.all().select_related(
                'user', 'flight__departure_airport', 'flight__arrival_airport'
            )

        return Ticket.objects.filter(user=user).select_related(
            'flight__departure_airport', 'flight__arrival_airport'
        )

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TicketSerializer
        return TicketCreateSerializer

    def get_permissions(self):
        """
        - Тільки аутентифіковані користувачі можуть бачити/створювати квитки.
        - Тільки адміни можуть редагувати/видаляти (за бажанням).
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return[IsAuthenticated()]

    def perform_create(self, serializer):
        """Прив'язуємо квиток до поточного користувача при створенні"""
        serializer.save(user=self.request.user)
