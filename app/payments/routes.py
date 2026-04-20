from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.orders.models import Order
from app.gateway.models import PaymentGateway

payments_bp = Blueprint("payments", __name__, url_prefix="/payment")

@payments_bp.route("/<int:order_id>")
@login_required
def payment(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template("payment.html", order=order)


@payments_bp.route("/start/<int:order_id>/<string:method>")
@login_required
def start_payment(order_id, method):
    order = Order.query.get_or_404(order_id)

    payment = PaymentGateway(
        order_id=order.id,
        user_id=current_user.id,
        amount=order.total_amount,
        method=method,
        status="initiated"
    )

    db.session.add(payment)
    db.session.commit()

    return redirect(url_for("gateway.gateway_ui", payment_id=payment.id))
