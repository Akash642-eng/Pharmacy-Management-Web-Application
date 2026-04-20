from flask import Blueprint, render_template
from datetime import date
from sqlalchemy import or_

from app.products.models import Product

products_bp = Blueprint("products", __name__)

@products_bp.route("/products-page")
def products_page():

    today = date.today()

    products = (
        Product.query
        .filter(
            Product.is_active.is_(True),
            or_(
                Product.expiry_date.is_(None),
                Product.expiry_date >= today
            )
        )
        .order_by(Product.created_at.desc())
        .all()
    )

    return render_template("products.html", products=products)
