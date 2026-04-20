from flask_login import current_user
from flask import redirect, url_for, flash
from functools import wraps
from datetime import date

from app.extensions import db


def customer_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please login to continue", "warning")
            return redirect(url_for("main.login_page"))

        if current_user.is_admin:
            flash("Admins cannot perform customer actions", "danger")
            return redirect(url_for("admin_panel.dashboard"))

        return f(*args, **kwargs)
    return wrapper

def validate_and_lock_stock(cart):
    """
    Absolute safety check before order creation.
    Prevents:
    - expired products
    - inactive products
    - insufficient stock
    Deducts stock atomically.
    """

    today = date.today()

    for item in cart.items:
        product = item.product

        if not product.is_active:
            raise ValueError(f"{product.name} is no longer available")

        if product.expiry_date and product.expiry_date < today:
            raise ValueError(f"{product.name} is expired")

        if product.stock < item.quantity:
            raise ValueError(
                f"Only {product.stock} units available for {product.name}"
            )

    for item in cart.items:
        product = item.product
        product.stock -= item.quantity

    db.session.flush()
