from flask import Blueprint, render_template, request
from flask_mail import Message
from app.extensions import mail

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    return render_template("home.html")

@main_bp.route("/login-page")
def login_page():
    next_page = request.args.get("next")
    return render_template("login.html", next=next_page)

@main_bp.route("/register-page")
def register_page():
    return render_template("register.html")

from flask_mail import Message
from app.extensions import mail

@main_bp.route("/test-email")
def test_email():
    try:
        msg = Message(
            subject="Test Email – Maruti Pharmacy",
            recipients=["speedyy6789@gmail.com"],
            body="If you received this, SMTP is working."
        )
        mail.send(msg)
        print("✅ Email sent successfully")
        return "Email sent successfully"
    except Exception as e:
        print("❌ Email sending failed:", e)
        return "Email failed"

