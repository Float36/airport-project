from django.contrib import admin

from .models import Order, Ticket


class TicketInline(admin.TabularInline):
    """
    Allows to view and edit tickets
    directly on the Orders page.
    """

    model = Ticket
    extra = 1  # Number of empty forms for adding new tickets
    autocomplete_fields = ("flight",)

    fields = ("flight", "passenger_first_name", "passenger_last_name", "seat", "status")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Connect tickets to order page
    inlines = [TicketInline]

    list_display = ("id", "user", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("id", "user__username")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("user",)

    fieldsets = (
        (None, {"fields": ("user", "status")}),
        ("Timestamps", {"fields": ("created_at",)}),
    )


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "get_order_id",
        "get_passenger_name",
        "flight",
        "seat",
        "status",
    )
    list_filter = ("status", "flight__departure_time")
    search_fields = (
        "passenger_first_name",
        "passenger_last_name",
        "flight__flight_number",
        "order__id",
    )
    autocomplete_fields = ("order", "flight")

    @admin.display(description="Order ID")
    def get_order_id(self, obj):
        return obj.order.id

    get_order_id.admin_order_field = "order"

    @admin.display(description="Passenger")
    def get_passenger_name(self, obj):
        return f"{obj.passenger_first_name} {obj.passenger_last_name}"
