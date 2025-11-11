import os

import logging

from django.shortcuts import render
import datetime
import stripe
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse, Http404
from rest_framework.views import APIView
from rest_framework import viewsets, mixins, status, serializers, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import Ticket, Order, Transaction
from .serializers import (
    TicketSerializer, OrderSerializer, OrderCreateSerializer, TransactionSerializer
)


logger = logging.getLogger("booking")
stripe.api_key = settings.STRIPE_SECRET_KEY

class AuditLoggingMixin:
    """
    Mixin for automatic logging CRUD
    """
    def get_user_str(self):
        """Get 'User: 1' or 'AnonymousUser'"""
        user = self.request.user
        if user and user.is_authenticated:
            return f"User {user.id} ({user.username})"
        return "AnonymousUser"

    def perform_create(self, serializer):
        super().perform_create(serializer)
        instance = serializer.instance
        logger.info(
            f"{self.get_user_str()} CREATED {instance.__class__.__name__} "
            f"(ID: {instance.id})"
        )

    def perform_update(self, serializer):
        super().perform_update(serializer)
        instance = serializer.instance
        logger.info(
            f"{self.get_user_str()} UPDATED {instance.__class__.__name__} "
            f"(ID: {instance.id})"
        )

    def perform_destroy(self, instance):
        obj_id = instance.id
        obj_class_name = instance.__class__.__name__

        super().perform_destroy(instance)

        logger.info(
            f"{self.get_user_str()} DELETED {obj_class_name} "
            f"(ID: {obj_id})"
        )

    def handle_exception(self, exc):
        """
        Logging for exception
        """
        response = super().handle_exception(exc)

        user_str = self.get_user_str()
        view_name = self.__class__.__name__
        action = self.action

        if isinstance(exc, serializers.ValidationError):
            # Err 400
            logger.warning(
                f"{user_str} Validation Failed (400) on {action} "
                f"in {view_name}: {exc.detail}"
            )

        elif isinstance(exc, (exceptions.PermissionDenied, exceptions.NotAuthenticated)):
            # Err 403/401
            logger.warning(
                f"{user_str} Access Denied (401/403) on {action} "
                f"in {view_name}: {exc.detail}"
            )

        elif isinstance(exc, Http404):
            # Err 404
            logger.warning(
                f"{user_str} Not Found (404) on {action} "
                f"in {view_name}: {exc.detail}"
            )

        else:
            # Other (500)
            logger.error(
                f"{user_str} Unhandled Server Error (500) on {action} "
                f"in {view_name}: {exc}",
                exc_info=True
            )

        return response

class OrderViewSet(
    AuditLoggingMixin,
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

        order = serializer.instance
        logger.info(
            f"Order {order.id} created successfully "
            f"for user {self.request.user.id}."
        )

    @action(
        methods=["POST"],
        detail=True,
        url_path="create-checkout-session",
        permission_classes=[IsAuthenticated],
    )
    def create_checkout_session(self, request, pk=None):
        order = self.get_object()
        user = request.user

        logger.debug(
            f"User {user.id} attempting to create checkout session "
            f"for Order {order.id}"
        )

        # Check if order is waiting for pending
        if order.status != Order.Status.PENDING:
            logger.warning(
                f"Payment attempt failed for Order {order.id} (user: {user.id}). "
                f"Reason: Order status is '{order.status}', not 'PENDING'."
            )
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

            logger.debug(
                f"[Order {order.id}] Processing ticket for flight {ticket.flight.id}. "
                f"Price found: {ticket_price}"
            )

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
            logger.critical(
                f"Failed to create PENDING transaction for Order {order.id} (user: {user.id}). "
                f"Error: {e}",
                exc_info=True  # Add full err traceback
            )
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

            logger.info(
                f"Stripe checkout session created successfully for Order {order.id} "
                f"(Transaction: {transaction_pending.id}). "
                f"Stripe Session ID: {checkout_session.id}"
            )
            return Response({'sessionId': checkout_session['id'], 'url': checkout_session.url})
        except Exception as e:
            logger.error(
                f"Stripe API Error for Order {order.id} (Transaction: {transaction_pending.id}). "
                f"Error: {e}",
                exc_info=True
            )
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TicketViewSet(
    AuditLoggingMixin,
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
        logger.debug("Stripe webhook received.")

        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        if not webhook_secret:
            logger.critical("STRIPE_WEBHOOK_SECRET is not set. Webhook cannot be processed.")
            return HttpResponse("Webhook secret not set", status=500)

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            logger.warning(f"Stripe webhook payload error (ValueError): {e}", exc_info=True)
            return HttpResponse(status=400)

        except stripe._error.SignatureVerificationError as e:
            logger.warning(f"Stripe webhook signature verification failed: {e}", exc_info=True)
            return HttpResponse(status=400)

        session = event['data']['object']
        metadata = session.get('metadata', {})
        order_id = metadata.get('order_id')
        transaction_id = metadata.get('transaction_id')

        if not order_id or not transaction_id:
            logger.error(
                f"Stripe webhook missing metadata. "
                f"Received order_id: {order_id}, transaction_id: {transaction_id}."
            )
            return HttpResponse("Missing metadata in webhook", status=400)


        # Update Order and Transaction  together or not at all
        try:
            with transaction.atomic():
                order = Order.objects.get(id=order_id)
                tx = Transaction.objects.get(id=transaction_id)

                # Checking if this webhook haven't already processed
                if tx.status != Transaction.Status.PENDING:
                    logger.info(
                        f"Webhook for Transaction {tx.id} (Order {order.id}) "
                        f"already processed. Current status: {tx.status}."
                    )
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
                    logger.info(
                        f"Order {order_id} PAID via Stripe. "
                        f"Transaction {tx.id} set to SUCCESS. "
                        f"Stripe Payment Intent: {tx.provider_transaction_id}"
                    )

                elif event['type'] == 'checkout.session.expired':
                    # Update transaction
                    tx.status = Transaction.Status.FAILED
                    tx.save()

                    # Update order
                    order.status = Order.Status.CANCELLED
                    order.save()
                    logger.warning(
                        f"Stripe checkout session for Order {order_id} EXPIRED. "
                        f"Transaction {tx.id} set to FAILED."
                    )

        except Order.DoesNotExist:
            logger.error(
                f"Stripe Webhook ERROR: Order.DoesNotExist for ID {order_id}. "
                f"Metadata: {metadata}"
            )
            return HttpResponse(status=404)
        except Transaction.DoesNotExist:
            logger.error(
                f"Stripe Webhook ERROR: Transaction.DoesNotExist for ID {transaction_id}. "
                f"Metadata: {metadata}"
            )
            return HttpResponse(status=404)
        except Exception as e:
            logger.critical(
                f"Stripe Webhook CRITICAL unknown error. Metadata: {metadata}. Error: {e}",
                exc_info=True
            )
            return HttpResponse(status=500)

        logger.info(
            f"Stripe webhook POST success"
        )
        return HttpResponse(status=200)





