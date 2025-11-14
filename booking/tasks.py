from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import Order


@shared_task
def send_success_email_task(order_id):
    """
    Task for asynchronously sending email
    """
    order = Order.objects.get(id=order_id)
    user = order.user

    # Make a tickets list
    tickets_info = []
    for ticket in order.tickets.all():
        tickets_info.append(
            f"- Квиток: {ticket.passenger_first_name} {ticket.passenger_last_name}, "
            f"- Рейс: {ticket.flight.flight_number}, "
            f"- Місце: {ticket.seat.row}{ticket.seat.seat}"
        )

    context = {
        "user_name": user.username,
        "order_id": order.id,
        "tickets_info": "\n".join(tickets_info),
    }

    message = render_to_string("booking/email/confirmation_email.txt", context)

    send_mail(
        f"Підтвердження замовлення #{order.id}",
        message,
        None,
        [user.email],
        fail_silently=False,
    )

    return f"Email sent for order {order_id}"
