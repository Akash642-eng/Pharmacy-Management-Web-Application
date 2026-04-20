from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date

from app.extensions import db
from app.cart.models import Cart, CartItem
from app.products.models import Product
from app.orders.utils import customer_required

cart_bp = Blueprint("cart", __name__)

@cart_bp.route("/cart")
@login_required
@customer_required
def view_cart():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    return render_template("cart.html", cart=cart)


@cart_bp.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
@customer_required
def add_to_cart(product_id):

    today = date.today()

    product = (
        Product.query
        .filter(
            Product.id == product_id,
            Product.is_active.is_(True),
            (
                Product.expiry_date.is_(None) |
                (Product.expiry_date >= today)
            )
        )
        .first()
    )

    if not product:
        flash("This product is no longer available", "danger")
        return redirect(url_for("products.products_page"))

    if product.stock <= 0:
        flash("This product is out of stock", "danger")
        return redirect(url_for("products.products_page"))

    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()

    item = CartItem.query.filter_by(
        cart_id=cart.id,
        product_id=product.id
    ).first()

    if item:
        if item.quantity + 1 > product.stock:
            flash(
                f"Only {product.stock} units available for {product.name}",
                "warning"
            )
            return redirect(url_for("cart.view_cart"))

        item.quantity += 1
    else:
        item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=1
        )
        db.session.add(item)

    db.session.commit()
    flash("Product added to cart", "success")
    return redirect(url_for("cart.view_cart"))

@cart_bp.route("/cart/update/<int:item_id>/<action>")
@login_required
@customer_required
def update_cart(item_id, action):

    item = CartItem.query.get_or_404(item_id)
    product = item.product
    today = date.today()


    if (
        not product.is_active or
        (product.expiry_date and product.expiry_date < today)
    ):
        db.session.delete(item)
        db.session.commit()
        flash(f"{product.name} is no longer available", "danger")
        return redirect(url_for("cart.view_cart"))

    if action == "inc":
        if item.quantity + 1 > product.stock:
            flash(
                f"Only {product.stock} units available for {product.name}",
                "warning"
            )
            return redirect(url_for("cart.view_cart"))

        item.quantity += 1

    elif action == "dec":
        item.quantity -= 1
        if item.quantity <= 0:
            db.session.delete(item)

    db.session.commit()
    return redirect(url_for("cart.view_cart"))
