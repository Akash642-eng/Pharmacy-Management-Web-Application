import os

from flask import Flask

from app.config import Config
from app.extensions import db, migrate, bcrypt, login_manager
from app.logging_config import configure_logging

from app.cart import models
from app.payments import models
from app.gateway import models

# Email
from app.extensions import mail


def create_app(test_config=None):
    app = Flask(__name__)

    # Base configuration
    app.config.from_object(Config)

    # Test/override configuration must happen BEFORE extensions initialize.
    if test_config:
        app.config.update(test_config)

    # Application logging
    configure_logging()

    # Email configuration
    app.config.update(
        MAIL_SERVER="smtp.gmail.com",
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USE_SSL=False,
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_DEFAULT_SENDER=(
            os.getenv("MAIL_DEFAULT_SENDER_NAME", "Maruti Pharmacy"),
            os.getenv("MAIL_USERNAME")
        )
    )

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Blueprints
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.products.routes import products_bp
    from app.orders.routes import orders_bp
    from app.admin.routes import admin_bp
    from app.payments.routes import payments_bp
    from app.cart.routes import cart_bp
    from app.gateway.routes import gateway_bp
    from app.health.routes import health_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)

    app.register_blueprint(admin_bp, name="admin_panel")

    app.register_blueprint(payments_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(gateway_bp)
    app.register_blueprint(health_bp)

    return app