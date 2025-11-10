import os

from django.shortcuts import render
import datetime
import stripe
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .models import Ticket, Order
from .serializers import (
    TicketSerializer, TicketCreateSerializer,
    OrderSerializer, OrderCreateSerializer
)


stripe.api_key = settings.STRIPE_SECRET_KEY


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

    @action(
        methods=["POST"],
        detail=True,
        url_path="create-checkout-session",
        permission_classes=[IsAuthenticated],
    )
    def create_checkout_session(self, request, pk=None):
        order = self.get_object()

        # Check if order is already paid
        if order.Status == Order.Status.PAID:
            return Response(
                {"error": "Order is already paid"},
                status=status.HTTP_400_BAD_REQUEST
            )

        expires_at_time = int(
            (datetime.datetime.now() + datetime.timedelta(minutes=30)).timestamp()
        )

        line_items = []
        for ticket in order.tickets.all():
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f"Ticket: {ticket.flight.flight_number}",
                        'description': (
                            f"Seat {ticket.seat.row}{ticket.seat.seat} for "
                            f"{ticket.passenger_first_name} {ticket.passenger_last_name}"
                        ),
                    },
                    'unit_amount': int(ticket.flight.price * 100),
                },
                'quantity': 1,
            })

        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=line_items,
                mode='payment',
                # Return order id to find it on webhook
                metadata={'order_id': order.id},
                # URL, where user is redirected
                success_url="http://example.com/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="http://example.com/cancel",

                expires_at=expires_at_time,
            )
            return Response({'sessionId': checkout_session['id'], 'url': checkout_session.url})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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



class StripeWebhookView(APIView):
    """
    Get msg from Stripe about success payment and update status
    """
    def post(self, request):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            return HttpResponse(status=400)

        except stripe._error.SignatureVerificationError as e:
            return HttpResponse(status=400)


        print("111111")
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            order_id = session.get('metadata', {}).get('order_id')
            print("22222")

            if order_id:
                print("333333")
                try:
                    print("444444")
                    order = Order.objects.get(id=order_id)
                    order.status = Order.Status.PAID
                    order.save()
                except Order.DoesNotExist:
                    return HttpResponse(status=404)

        elif event['type'] == 'checkout.session.expired':
            session = event['data']['object']
            order_id = session.get('metadata', {}).get('order_id')

            if order_id:
                try:
                    order = Order.objects.get(id=order_id)
                    if order.status == Order.Status.PENDING:
                        order.status = Order.Status.CANCELLED
                        order.save()
                        print(f"Order {order_id} status updated to CANCELLED!")
                except Order.DoesNotExist:
                    print(f"ERROR: Order with id={order_id} not found.")
                    return HttpResponse(status=404)

        return HttpResponse(status=200)




