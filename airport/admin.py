from django.contrib import admin

from .models import Airline, Airplane, Airport, City, Country, Flight


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    search_fields = ("name", "country__name")
    list_filter = ("country",)
    autocomplete_fields = ("country",)


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("name", "iata_code", "city", "get_country")
    search_fields = ("name", "iata_code", "city__name")
    list_filter = ("city__country",)  # filter by country
    autocomplete_fields = ("city",)

    @admin.display(description="Country")
    def get_country(self, obj):
        return obj.city.country.name

    get_country.admin_order_field = "city__country"


@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ("name", "home_base")
    search_fields = ("name",)
    autocomplete_fields = ("home_base",)


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ("model", "airline")
    search_fields = ("model",)
    list_filter = ("airline",)
    autocomplete_fields = ("airline",)


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        "flight_number",
        "departure_airport",
        "arrival_airport",
        "departure_time",
        "arrival_time",
        "status",
    )
    search_fields = (
        "flight_number",
        "departure_airport__name",
        "arrival_airport__name",
    )
    list_filter = ("status", "departure_time", "airplane__airline")
    autocomplete_fields = ("departure_airport", "arrival_airport", "airplane")
