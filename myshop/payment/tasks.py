from io import BytesIO
import weasyprint
from celery import shared_task
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings

from orders.models import Order


@shared_task
def payment_completed(order_id: int):
    """Task to send an e-mail notification when an order is successfully paid."""
    order = Order.objects.get(id=order_id)

    # Create invoice email
    subject = f"My Shop - Invoice no. {order.id}"
    message = "Please, find attached the invoice for your recent purchase."
    email = EmailMessage(subject, message, "anhimovn1@gmail.com", [order.email])

    # Generate PDF
    html = render_to_string("orders/order/pdf.html", {"order": order})
    out = BytesIO()
    weasyprint.HTML(string=html).write_pdf(
        out, stylesheets=[weasyprint.CSS(settings.STATIC_ROOT / "css/pdf.css")]
    )

    # Add PDF to email
    email.attach(f"order_{order.id}.pdf", out.getvalue(), "application/pdf")

    # Send email
    email.send()
