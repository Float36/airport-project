from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CountryViewSet, AirportViewSet, AirlineViewSet,
    AirplaneViewSet, FlightViewSet
)

router = DefaultRouter()
router.register(r'countries', CountryViewSet)
router.register(r'airports', AirportViewSet)
router.register(r'airlines', AirlineViewSet)
router.register(r'airplanes', AirplaneViewSet)
router.register(r'flights', FlightViewSet)

urlpatterns = [
    path('', include(router.urls)),
]