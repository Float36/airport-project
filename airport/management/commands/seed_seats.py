from django.core.management.base import BaseCommand
from airport.models import AirplaneType, Seat
from django.db import transaction


SEAT_BLUEPRINTS = {
    "Boeing 737": {
        "rows": range(1, 31),
        "seats": ['A', 'B', 'C', 'D', 'E', 'F'],
        "default_type": Seat.SeatType.ECONOMY,
    },
    "Airbus A320": {
        "rows": range(1, 26),
        "seats": ['A', 'B', 'C', 'D', 'E', 'F'],
        "default_type": Seat.SeatType.ECONOMY,
    },
}


class Command(BaseCommand):
    help = "Seeds the database with airplane types and their seat layouts."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting to seed seats..."))

        total_seats_created = 0

        # 1. Go through each "drawing"
        for type_name, config in SEAT_BLUEPRINTS.items():

            # 2. Find or create an Aircraft Type
            plane_type, created = AirplaneType.objects.get_or_create(
                name=type_name
            )

            if created:
                self.stdout.write(f"Created AirplaneType: {type_name}")
            else:
                self.stdout.write(f"Found existing AirplaneType: {type_name}")

            # 3. Creating space for this type of aircraft
            seats_created_for_type = 0
            for row_num in config["rows"]:
                for seat_char in config["seats"]:

                    # 4. Used get_or_create for seats
                    seat, seat_created = Seat.objects.get_or_create(
                        airplane_type=plane_type,
                        row=row_num,
                        seat=seat_char,
                        defaults={'seat_type': config["default_type"]}
                    )

                    if seat_created:
                        seats_created_for_type += 1
                        total_seats_created += 1

            if seats_created_for_type > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  -> Created {seats_created_for_type} new seats for {type_name}."
                    )
                )
            else:
                self.stdout.write(
                    f"  -> All seats for {type_name} already exist."
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSeeding complete. Created {total_seats_created} new seats in total."
            )
        )