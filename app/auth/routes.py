from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from app.extensions import db, bcrypt
from app.auth.models import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    if not name or not email or not password:
        flash("All fields are required", "danger")
        return redirect(url_for("main.register_page"))

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash("Email already registered", "danger")
        return redirect(url_for("main.register_page"))

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(
        name=name,
        email=email,
        password_hash=hashed_password
    )

    db.session.add(user)
    db.session.commit()

    flash("Registration successful. Please login.", "success")
    return redirect(url_for("main.login_page"))

@auth_bp.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        flash("Invalid email or password", "danger")
        return redirect(url_for("main.login_page"))

    login_user(user)

    next_page = request.args.get("next")

    flash("Login successful", "success")
    return redirect(next_page or url_for("main.home"))

@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for("main.login_page"))
