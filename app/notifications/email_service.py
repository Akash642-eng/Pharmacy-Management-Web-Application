from flask import render_template
from flask_mail import Message
from app.extensions import mail
from datetime import datetime
from app.orders.invoice import generate_invoice_pdf

def send_order_confirmation_email(order):
    if order.payment_status != "success":
        return

    html_body = render_template(
        "email/order_confirmation.html",
        user_name=order.user.name,
        order_id=order.id,
        order_date=order.created_at.strftime("%d %b %Y"),
        total_amount=f"{order.total_amount:.2f}",
        year=datetime.now().year
    )

    msg = Message(
        subject=f"Order Confirmed – #{order.id} | Maruti Pharmacy",
        recipients=[order.user.email],
        html=html_body
    )

    pdf_buffer = generate_invoice_pdf(order)
    msg.attach(
        filename=f"invoice_{order.invoice_number}.pdf",
        content_type="application/pdf",
        data=pdf_buffer.getvalue()
    )

    mail.send(msg)
