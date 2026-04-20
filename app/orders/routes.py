from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file
from flask_login import login_required, current_user
from datetime import datetime, date   # ✅ date added (REQUIRED)
import random
import io

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

from app.extensions import db
from app.orders.models import Order, OrderItem
from app.cart.models import Cart
from app.orders.utils import customer_required, validate_and_lock_stock
from app.notifications.email_service import send_order_confirmation_email
from app.orders.invoice import generate_invoice_pdf

orders_bp = Blueprint("orders", __name__)

BRAND_GREEN = HexColor("#198754")


@orders_bp.route("/checkout", methods=["GET", "POST"])
@login_required
@customer_required
def checkout():
    cart = Cart.query.filter_by(user_id=current_user.id).first()

    if not cart or not cart.items:
        flash("Your cart is empty", "danger")
        return redirect(url_for("products.products_page"))

    if request.method == "POST":
        address = request.form.get("address")
        phone = request.form.get("phone")
        payment_method = request.form.get("payment_method")

        if not address or not phone or not payment_method:
            flash("All fields are required", "danger")
            return redirect(url_for("orders.checkout"))

        try:
            validate_and_lock_stock(cart)
        except ValueError as e:
            db.session.rollback()
            flash(str(e), "danger")
            return redirect(url_for("cart.view_cart"))


        order = Order(
            user_id=current_user.id,
            address=address,
            phone=phone,
            total_amount=cart.total_amount(),
            payment_method=payment_method,
            status="pending_payment",
            payment_status="pending"
        )

        db.session.add(order)
        db.session.flush()

        for item in cart.items:
            db.session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.product.price
                )
            )

        if payment_method == "cod":
            payment_success = True
        else:
            payment_success = random.choice([True, False])

        if payment_success:
            order.payment_status = "success"
            order.status = "processing" if payment_method == "cod" else "paid"
            order.invoice_number = f"INV-{order.id}-{datetime.utcnow().strftime('%Y%m%d')}"

            db.session.delete(cart)

        else:
            order.payment_status = "failed"
            order.status = "failed"

            db.session.rollback()
            flash("Payment failed. Stock restored.", "danger")
            return redirect(url_for("cart.view_cart"))

        db.session.commit()

        if order.payment_status == "success":
            try:
                send_order_confirmation_email(order)
            except Exception as e:
                print("Email error:", e)

        return redirect(
            url_for(
                "orders.order_success" if payment_success else "orders.order_failed",
                order_id=order.id
            )
        )

    return render_template("checkout.html", cart=cart)


@orders_bp.route("/orders")
@login_required
@customer_required
def my_orders():
    orders = (
        Order.query
        .filter_by(user_id=current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return render_template("orders.html", orders=orders)

@orders_bp.route("/order/success/<int:order_id>")
@login_required
@customer_required
def order_success(order_id):
    order = Order.query.get_or_404(order_id)

    if order.user_id != current_user.id:
        return redirect(url_for("main.home"))

    return render_template("order_success.html", order=order)

@orders_bp.route("/order/failed/<int:order_id>")
@login_required
@customer_required
def order_failed(order_id):
    order = Order.query.get_or_404(order_id)

    if order.user_id != current_user.id:
        return redirect(url_for("main.home"))

    return render_template("order_failed.html", order=order)

@orders_bp.route("/order/<int:order_id>/invoice")
@login_required
def download_invoice(order_id):
    order = Order.query.get_or_404(order_id)

    if not current_user.is_admin and order.user_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for("main.home"))

    pdf_buffer = generate_invoice_pdf(order)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"invoice_{order.invoice_number}.pdf",
        mimetype="application/pdf"
    )
