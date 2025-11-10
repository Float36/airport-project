import os

from django.shortcuts import render
import datetime
import stripe
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import Ticket, Order, Transaction
from .serializers import (
    TicketSerializer, OrderSerializer, OrderCreateSerializer, TransactionSerializer
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

    permission_classes = [IsAuthenticated]

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
            'tickets__flight__airplane__airplane_type',
            'transaction'
        )

        if user.is_staff or (hasattr(user, 'role') and user.role == 'ADMIN'):
            return base_queryset.all()

        return base_queryset.filter(user=user)

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

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

        # Check if order is waiting for pending
        if order.status != Order.Status.PENDING:
            return Response(
                {"error": "This order cannot be paid. It's already paid or cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )

        expires_at_time = int(
            (datetime.datetime.now() + datetime.timedelta(minutes=30)).timestamp()
        )

        line_items = []
        total_amount = Decimal("0.00")

        for ticket in order.tickets.all():
            ticket_price = ticket.flight.price
            total_amount += ticket_price

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


        # Create a PENDING transaction before creating a Stripe session
        try:
            transaction_pending = Transaction.objects.create(
                order=order,
                amount=total_amount,
                currency="usd",
                status=Transaction.Status.PENDING
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to create local transaction: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Create Stripe session
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=line_items,
                mode='payment',
                # Return order id to find it on webhook
                metadata={'order_id': order.id, 'transaction_id': transaction_pending.id},
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


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    VeiwSet for Transactions, only for admin
    """
    queryset = Transaction.objects.all().select_related("order__user")
    serializer_class = TransactionSerializer
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

        if not webhook_secret:
            return HttpResponse("Webhook secret not set", status=500)

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            return HttpResponse(status=400)

        except stripe._error.SignatureVerificationError as e:
            return HttpResponse(status=400)

        session = event['data']['object']
        metadata = session.get('metadata', {})
        order_id = metadata.get('order_id')
        transaction_id = metadata.get('transaction_id')

        if not order_id or not transaction_id:
            return HttpResponse("Missing metadata in webhook", status=400)


        # Use transaction.atomic so Order and Transaction updates together or not at all
        try:
            with transaction.atomic():
                order = Order.objects.get(id=order_id)
                tx = Transaction.objects.get(id=transaction_id)

                # Checking if this webhook haven't already processed
                if tx.status != Transaction.Status.PENDING:
                    return HttpResponse(f"Transaction {tx.id} already processed.", status=200)

                if event['type'] == 'checkout.session.completed':
                    # Update transaction
                    tx.status = Transaction.Status.SUCCESS
                    # Save id from Stripe
                    tx.provider_transaction_id = session.get('payment_intent') or session.id
                    tx.save()

                    # Update order
                    order.status = Order.Status.PAID
                    order.save()

                    print(f"Order {order_id} PAID. Transaction {tx.id} SUCCESS.")

                elif event['type'] == 'checkout.session.expired':
                    # Update transaction
                    tx.status = Transaction.Status.FAILED
                    tx.save()

                    # Update order
                    order.status = Order.Status.CANCELLED
                    order.save()
                    print(f"Order {order_id} CANCELLED. Transaction {tx.id} FAILED.")

        except Order.DoesNotExist:
            print(f"ERROR: Webhook for non-existent Order ID {order_id}")
            return HttpResponse(status=404)
        except Transaction.DoesNotExist:
            print(f"ERROR: Webhook for non-existent Transaction ID {transaction_id}")
            return HttpResponse(status=404)
        except Exception as e:
            print(f"ERROR processing webhook: {e}")
            return HttpResponse(status=500)

        return HttpResponse(status=200)





