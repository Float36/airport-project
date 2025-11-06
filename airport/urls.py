from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CountryViewSet, CityViewSet, AirportViewSet,
    AirlineViewSet, AirplaneViewSet, FlightViewSet,
    SeatViewSet, AirplaneTypeViewSet
)

router = DefaultRouter()
router.register(r'countries', CountryViewSet)
router.register(r'cities', CityViewSet)
router.register(r'airports', AirportViewSet)
router.register(r'airlines', AirlineViewSet)
router.register(r'airplanes', AirplaneViewSet)
router.register(r'flights', FlightViewSet)
router.register(r'seats', SeatViewSet)
router.register(r'airplanetype', AirplaneTypeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]