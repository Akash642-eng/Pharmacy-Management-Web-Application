from datetime import date

from flask import Blueprint, render_template
from sqlalchemy import or_

from app.cache import (
    get_cached_product_catalog,
    set_cached_product_catalog,
)
from app.products.models import Product

products_bp = Blueprint("products", __name__)


@products_bp.route("/products-page")
def products_page():
    products = get_cached_product_catalog()

    if products is None:
        today = date.today()

        records = (
            Product.query
            .filter(
                Product.is_active.is_(True),
                or_(
                    Product.expiry_date.is_(None),
                    Product.expiry_date >= today,
                ),
            )
            .order_by(Product.created_at.desc())
            .all()
        )

        products = [
            {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "stock": product.stock,
                "category": product.category,
                "description": product.description,
                "image_url": product.image_url,
                "is_offer": product.is_offer,
            }
            for product in records
        ]

        set_cached_product_catalog(products)

    return render_template(
        "products.html",
        products=products,
    )