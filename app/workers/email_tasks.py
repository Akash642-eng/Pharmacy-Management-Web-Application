from flask import current_app
from rq import get_current_job

from app.extensions import db
from app.orders.models import Order
from app.notifications.email_service import send_order_confirmation_email


def send_order_confirmation(order_id):
    """Send confirmation for a committed, successfully paid order."""
    job = get_current_job()
    current_app.logger.info(
        "Processing order confirmation: order_id=%s job_id=%s",
        order_id,
        job.id if job else None,
    )

    try:
        order = db.session.get(Order, order_id)

        if order is None:
            current_app.logger.warning(
                "Order confirmation skipped: order_id=%s not found",
                order_id,
            )
            return

        if order.payment_status != "success":
            current_app.logger.info(
                "Order confirmation skipped: order_id=%s payment_status=%s",
                order_id,
                order.payment_status,
            )
            return

        send_order_confirmation_email(order)

        current_app.logger.info(
            "Order confirmation email sent: order_id=%s",
            order_id,
        )
    finally:
        db.session.remove()
