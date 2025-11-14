from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet, StripeWebhookView, TicketViewSet, TransactionViewSet

router = DefaultRouter()

router.register(r"tickets", TicketViewSet, basename="ticket")
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"transactions", TransactionViewSet, basename="transaction")

urlpatterns = [
    path("", include(router.urls)),
    path("stripe-webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
]
