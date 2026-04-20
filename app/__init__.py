from flask import Flask
from app.config import Config
from app.extensions import db, migrate, bcrypt, login_manager
 
from app.cart import models
from app.payments import models
from app.gateway import models

#email
from app.extensions import mail


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)


    #email
    app.config.update(
        MAIL_SERVER = "smtp.gmail.com",
        MAIL_PORT = 587,
        MAIL_USE_TLS = True,
        MAIL_USE_SSL = False,
        MAIL_USERNAME = "speedyy6789@gmail.com",
        MAIL_PASSWORD = "znjgohuyvlnjrtzc",
        MAIL_DEFAULT_SENDER = ("Maruti Pharmacy", "speedyy6789@gmail.com")
    )


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

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)

    app.register_blueprint(admin_bp, name="admin_panel")

    app.register_blueprint(payments_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(gateway_bp)

    return app