from flask import Blueprint, render_template, request, Response, redirect, url_for, flash
from flask_login import login_required
from datetime import date, datetime
from sqlalchemy import func
from werkzeug.utils import secure_filename
import os

from app.admin.utils import admin_required
from app.extensions import db
from app.auth.models import User
from app.orders.models import Order
from app.products.models import Product
from flask import current_app

admin_bp = Blueprint(
    "admin_panel",
    __name__,
    url_prefix="/admin"
)

@admin_bp.route("/")
@login_required
@admin_required
def dashboard():

    total_orders = Order.query.count()

    today_str = date.today().strftime("%Y-%m-%d")
    today_date = date.today()

    today_orders = Order.query.filter(
        Order.created_at.isnot(None),
        func.strftime("%Y-%m-%d", Order.created_at) == today_str
    ).count()

    pending_orders = Order.query.filter(
        Order.status.in_(["pending_payment", "processing", "shipped"])
    ).count()

    total_revenue = (
        db.session.query(func.coalesce(func.sum(Order.total_amount), 0))
        .filter(Order.payment_status == "success")
        .scalar()
    )

    total_customers = User.query.filter(
        (User.role == "user") | (User.role.is_(None))
    ).count()

    expired_products = (
        Product.query
        .filter(
            Product.is_active.is_(True),
            Product.expiry_date.isnot(None),
            Product.expiry_date < today_date
        )
        .order_by(Product.expiry_date.asc())
        .all()
    )

    low_stock_products = (
        Product.query
        .filter(
            Product.is_active.is_(True),
            Product.stock <= Product.reorder_level,
            (
                Product.expiry_date.is_(None) |
                (Product.expiry_date >= today_date)
            )
        )
        .order_by(Product.stock.asc())
        .all()
    )

    return render_template(
        "admin/dashboard.html",
        total_orders=total_orders,
        today_orders=today_orders,
        pending_orders=pending_orders,
        total_revenue=total_revenue,
        total_customers=total_customers,
        expired_products=expired_products,
        expired_count=len(expired_products),
        low_stock_products=low_stock_products,
        low_stock_count=len(low_stock_products)
    )

@admin_bp.route("/orders")
@login_required
@admin_required
def orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin/orders.html", orders=orders)


@admin_bp.route("/orders/<int:order_id>", methods=["GET", "POST"])
@login_required
@admin_required
def order_detail(order_id):

    order = Order.query.get_or_404(order_id)

    ALLOWED_STATUSES = [
        "pending_payment",
        "processing",
        "shipped",
        "delivered",
        "failed",
        "cancelled"
    ]

    if request.method == "POST":
        new_status = request.form.get("status")
        if new_status in ALLOWED_STATUSES:
            order.status = new_status
            db.session.commit()
            flash("Order status updated", "success")

    return render_template(
        "admin/order_detail.html",
        order=order,
        allowed_statuses=ALLOWED_STATUSES
    )


@admin_bp.route("/products")
@login_required
@admin_required
def products():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template("admin/products.html", products=products)


@admin_bp.route("/products/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_product():

    if request.method == "POST":
        name = request.form.get("name")
        price = request.form.get("price")
        stock = request.form.get("stock")
        category = request.form.get("category")
        description = request.form.get("description")
        image_file = request.files.get("image")

        expiry_date_raw = request.form.get("expiry_date")
        expiry_date_value = None

        if expiry_date_raw:
            try:
                expiry_date_value = date.fromisoformat(expiry_date_raw)
            except ValueError:
                flash("Invalid expiry date format", "danger")
                return redirect(url_for("admin_panel.add_product"))

        if not all([name, price, stock, category]):
            flash("All required fields must be filled", "danger")
            return redirect(url_for("admin_panel.add_product"))

        if not image_file or image_file.filename == "":
            flash("Product image is required", "danger")
            return redirect(url_for("admin_panel.add_product"))

        filename = secure_filename(image_file.filename)

        upload_folder = os.path.join(
            current_app.root_path,
            "static",
            "images",
            "products"
        )

        os.makedirs(upload_folder, exist_ok=True)

        image_path = os.path.join(upload_folder, filename)
        image_file.save(image_path)

        image_url = f"images/products/{filename}"

        product = Product(
            name=name,
            price=float(price),
            stock=int(stock),
            category=category,
            description=description,
            image_url=image_url,
            expiry_date=expiry_date_value
        )

        db.session.add(product)
        db.session.commit()

        flash("Product added successfully", "success")
        return redirect(url_for("admin_panel.products"))

    return render_template("admin/add_product.html")


@admin_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        product.name = request.form.get("name")
        product.price = float(request.form.get("price"))
        product.stock = int(request.form.get("stock"))
        product.category = request.form.get("category")
        product.description = request.form.get("description")

        expiry_date_raw = request.form.get("expiry_date")
        if expiry_date_raw:
            try:
                product.expiry_date = date.fromisoformat(expiry_date_raw)
            except ValueError:
                flash("Invalid expiry date format", "danger")
                return redirect(url_for("admin_panel.edit_product", product_id=product.id))
        else:
            product.expiry_date = None

        image_file = request.files.get("image")
        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(current_app.root_path, "static", "images", "products")
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, filename)
            image_file.save(image_path)
            product.image_url = f"images/products/{filename}"

        db.session.commit()
        flash("Product updated successfully", "success")
        return redirect(url_for("admin_panel.products"))

    return render_template("admin/edit_product.html", product=product)

@admin_bp.route("/customers")
@login_required
@admin_required
def customers():

    customers = (
        db.session.query(
            User,
            func.count(Order.id).label("order_count")
        )
        .outerjoin(Order, Order.user_id == User.id)
        .filter(
            (User.role == "user") | (User.role.is_(None))
        )
        .group_by(User.id)
        .order_by(User.created_at.desc())
        .all()
    )

    return render_template("admin/customers.html", customers=customers)

@admin_bp.route("/invoices")
@login_required
@admin_required
def invoices():

    invoices = (
        Order.query
        .filter(Order.invoice_number.isnot(None))
        .order_by(Order.created_at.desc())
        .all()
    )

    return render_template("admin/invoices.html", invoices=invoices)

@admin_bp.route("/reports")
@login_required
@admin_required
def reports():

    total_revenue = (
        db.session.query(func.coalesce(func.sum(Order.total_amount), 0))
        .filter(Order.status.in_(["paid", "cod", "delivered"]))
        .scalar()
    )

    status_counts = (
        db.session.query(Order.status, func.count(Order.id))
        .group_by(Order.status)
        .all()
    )

    payment_counts = (
        db.session.query(Order.payment_method, func.count(Order.id))
        .group_by(Order.payment_method)
        .all()
    )

    daily_orders = (
        db.session.query(
            func.date(Order.created_at),
            func.count(Order.id)
        )
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at).desc())
        .limit(7)
        .all()
    )

    return render_template(
        "admin/reports.html",
        total_revenue=total_revenue,
        status_counts=status_counts,
        payment_counts=payment_counts,
        daily_orders=daily_orders
    )


@admin_bp.route("/reports/export/orders")
@login_required
@admin_required
def export_orders_csv():

    orders = Order.query.order_by(Order.created_at.desc()).all()

    def generate():
        yield "Order ID,Customer ID,Total Amount,Payment Method,Payment Status,Order Status,Created At\n"
        for o in orders:
            yield f"{o.id},{o.user_id},{o.total_amount},{o.payment_method},{o.payment_status},{o.status},{o.created_at}\n"

    return Response(generate(), mimetype="text/csv")


@admin_bp.route("/reports/export/revenue")
@login_required
@admin_required
def export_revenue_csv():

    orders = Order.query.filter(
        Order.status.in_(["paid", "cod", "delivered"])
    ).all()

    def generate():
        yield "Order ID,Amount,Status,Date\n"
        for o in orders:
            yield f"{o.id},{o.total_amount},{o.status},{o.created_at.date()}\n"

    return Response(generate(), mimetype="text/csv")


@admin_bp.route("/reports/export/customers")
@login_required
@admin_required
def export_customers_csv():

    users = User.query.filter(User.role != "admin").all()

    def generate():
        yield "User ID,Name,Email,Joined Date\n"
        for u in users:
            yield f"{u.id},{u.name},{u.email},{u.created_at.date()}\n"

    return Response(generate(), mimetype="text/csv")


@admin_bp.route("/products/<int:product_id>/toggle-status", methods=["POST"])
@login_required
@admin_required
def toggle_product_status(product_id):

    product = Product.query.get_or_404(product_id)

    product.is_active = not product.is_active
    db.session.commit()

    status = "activated" if product.is_active else "deactivated"
    flash(f"Product {status} successfully", "success")

    return redirect(url_for("admin_panel.products"))


@admin_bp.route("/products/<int:product_id>/toggle-offer", methods=["POST"])
@login_required
@admin_required
def toggle_product_offer(product_id):

    product = Product.query.get_or_404(product_id)

    product.is_offer = not product.is_offer
    db.session.commit()

    status = "marked as offer" if product.is_offer else "removed from offers"
    flash(f"Product {status}", "success")

    return redirect(url_for("admin_panel.products"))


@admin_bp.route("/products/<int:product_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_product(product_id):

    product = Product.query.get_or_404(product_id)
    product.is_active = not product.is_active
    db.session.commit()

    flash(
        f"Product {'enabled' if product.is_active else 'disabled'} successfully",
        "success"
    )

    return redirect(url_for("admin_panel.products"))