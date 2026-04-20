from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app.extensions import db
from app.gateway.models import PaymentGateway
import random

gateway_bp = Blueprint("gateway", __name__, url_prefix="/gateway")

@gateway_bp.route("/ui/<int:payment_id>")
@login_required
def gateway_ui(payment_id):
    payment = PaymentGateway.query.get_or_404(payment_id)
    return render_template("gateway_ui.html", payment=payment)

@gateway_bp.route("/otp/<int:payment_id>")
@login_required
def gateway_otp(payment_id):
    payment = PaymentGateway.query.get_or_404(payment_id)

    otp = str(random.randint(100000, 999999))
    payment.otp = otp
    payment.status = "otp_sent"
    db.session.commit()

    print(f"[GATEWAY OTP] Payment {payment.id} → OTP: {otp}")

    return render_template("gateway_otp.html", payment=payment)

@gateway_bp.route("/verify/<int:payment_id>", methods=["POST"])
@login_required
def verify_otp(payment_id):
    payment = PaymentGateway.query.get_or_404(payment_id)
    entered_otp = request.form.get("otp")

    if entered_otp == payment.otp:
        payment.status = "success"
        db.session.commit()
        flash("Payment successful 🎉", "success")
        return redirect(url_for("orders.order_success", order_id=payment.order_id))

    payment.status = "failed"
    db.session.commit()
    flash("Invalid OTP. Payment failed ❌", "danger")
    return redirect(url_for("gateway.gateway_ui", payment_id=payment.id))
