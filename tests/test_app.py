
import re

import pytest

from app.auth.models import User
from app.cart.models import Cart, CartItem
from app.extensions import bcrypt, db
from app.gateway.models import PaymentGateway
from app.orders.models import Order
from app.products.models import Product


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

def create_user(
    name="Test User",
    email="user@example.com",
    password="Test@12345",
    role="user",
    is_admin=False,
):
    user = User(
        name=name,
        email=email,
        password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
        role=role,
        is_admin=is_admin,
    )

    db.session.add(user)
    db.session.commit()

    return user


def login(client, email="user@example.com", password="Test@12345"):
    return client.post(
        "/login",
        data={
            "email": email,
            "password": password,
        },
        follow_redirects=False,
    )


def create_product(
    name="Paracetamol 500mg",
    price=50.0,
    stock=10,
    category="Medicine",
):
    product = Product(
        name=name,
        price=price,
        stock=stock,
        category=category,
        description="Test pharmacy product",
        is_active=True,
    )

    db.session.add(product)
    db.session.commit()

    return product


# ---------------------------------------------------------------------------
# Application startup / public pages
# ---------------------------------------------------------------------------

def test_app_starts(app):
    assert app is not None
    assert app.name == "app"


@pytest.mark.parametrize(
    "url",
    [
        "/",
        "/login-page",
        "/register-page",
    ],
)
def test_public_pages(client, url):
    response = client.get(url)

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def test_user_registration(client, app):
    response = client.post(
        "/register",
        data={
            "name": "Alice",
            "email": "alice@example.com",
            "password": "Test@12345",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/login-page" in response.headers["Location"]

    with app.app_context():
        user = User.query.filter_by(
            email="alice@example.com"
        ).first()

        assert user is not None
        assert user.name == "Alice"


def test_duplicate_registration_is_rejected(client, app):
    create_user(
        name="Existing User",
        email="existing@example.com",
    )

    response = client.post(
        "/register",
        data={
            "name": "Another User",
            "email": "existing@example.com",
            "password": "Test@12345",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/register-page" in response.headers["Location"]


def test_valid_login(client):
    create_user()

    response = login(client)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_invalid_login_is_rejected(client):
    create_user()

    response = login(
        client,
        password="WrongPassword",
    )

    assert response.status_code == 302
    assert "/login-page" in response.headers["Location"]


def test_logout(client):
    create_user()

    login(client)

    response = client.get(
        "/logout",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/login-page" in response.headers["Location"]


# ---------------------------------------------------------------------------
# Authorization
# ---------------------------------------------------------------------------

def test_admin_requires_authentication(client):
    response = client.get("/admin/")

    assert response.status_code == 302
    assert "/login-page" in response.headers["Location"]


def test_customer_cannot_access_admin(client):
    create_user()

    login(client)

    response = client.get(
        "/admin/",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_admin_cannot_use_customer_cart(client):
    create_user(
        name="Admin User",
        email="admin@example.com",
        role="admin",
        is_admin=True,
    )

    login(
        client,
        email="admin@example.com",
    )

    response = client.get(
        "/cart",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/admin/" in response.headers["Location"]


def test_authenticated_customer_can_access_cart(client):
    create_user()

    login(client)

    response = client.get("/cart")

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

def test_products_page_shows_active_product(client, app):
    product = create_product()

    response = client.get("/products-page")

    assert response.status_code == 200
    assert product.name.encode() in response.data
    assert b"No image available" in response.data


def test_expired_product_is_not_listed(client):
    from datetime import date, timedelta

    product = Product(
        name="Expired Medicine",
        price=100.0,
        stock=5,
        category="Medicine",
        is_active=True,
        expiry_date=date.today() - timedelta(days=1),
    )

    db.session.add(product)
    db.session.commit()

    response = client.get("/products-page")

    assert response.status_code == 200
    assert b"Expired Medicine" not in response.data


# ---------------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------------

def test_customer_can_add_product_to_cart(client):
    create_user()
    product = create_product()

    login(client)

    response = client.post(
        f"/cart/add/{product.id}",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/cart" in response.headers["Location"]

    cart = Cart.query.filter_by(
        user_id=1
    ).first()

    assert cart is not None
    assert len(cart.items) == 1
    assert cart.items[0].product_id == product.id
    assert cart.items[0].quantity == 1


def test_adding_same_product_increases_quantity(client):
    create_user()
    create_product(stock=10)

    product = Product.query.first()

    login(client)

    client.post(f"/cart/add/{product.id}")
    client.post(f"/cart/add/{product.id}")

    cart = Cart.query.filter_by(
        user_id=1
    ).first()

    assert cart is not None
    assert len(cart.items) == 1
    assert cart.items[0].quantity == 2


def test_out_of_stock_product_cannot_be_added(client):
    create_user()
    product = create_product(stock=0)

    login(client)

    response = client.post(
        f"/cart/add/{product.id}",
        follow_redirects=False,
    )

    assert response.status_code == 302

    cart = Cart.query.filter_by(
        user_id=1
    ).first()

    assert cart is None


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

def test_customer_can_checkout_with_cod(client, monkeypatch):
    user = create_user()
    product = create_product(
        price=100.0,
        stock=5,
    )

    login(client)

    client.post(f"/cart/add/{product.id}")

    # Mock the queue so this unit test does not require Redis.
    monkeypatch.setattr(
        "app.orders.routes.enqueue_order_confirmation",
        lambda order_id: type("FakeJob", (), {"id": "test-job"})(),
    )

    response = client.post(
        "/checkout",
        data={
            "address": "Test Address",
            "phone": "9876543210",
            "payment_method": "cod",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/order/success/" in response.headers["Location"]

    order = Order.query.filter_by(
        user_id=user.id
    ).first()

    assert order is not None
    assert order.payment_method == "cod"
    assert order.payment_status == "success"
    assert order.status == "processing"

    refreshed_product = db.session.get(
        Product,
        product.id,
    )

    assert refreshed_product.stock == 4


def test_customer_can_view_own_orders(client):
    user = create_user()

    order = Order(
        user_id=user.id,
        total_amount=100.0,
        status="processing",
        payment_method="cod",
        payment_status="success",
    )

    db.session.add(order)
    db.session.commit()

    login(client)

    response = client.get("/orders")

    assert response.status_code == 200


def test_customer_cannot_view_another_users_order(client):
    owner = create_user(
        name="Owner",
        email="owner@example.com",
    )

    create_user(
        name="Other User",
        email="other@example.com",
    )

    order = Order(
        user_id=owner.id,
        total_amount=100.0,
        status="processing",
        payment_method="cod",
        payment_status="success",
    )

    db.session.add(order)
    db.session.commit()

    login(
        client,
        email="other@example.com",
    )

    response = client.get(
        f"/order/success/{order.id}",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


# ---------------------------------------------------------------------------
# Payments / simulated gateway
# ---------------------------------------------------------------------------

def test_authenticated_user_can_start_payment(client):
    user = create_user()

    order = Order(
        user_id=user.id,
        total_amount=250.0,
        status="pending_payment",
        payment_method="upi",
        payment_status="pending",
    )

    db.session.add(order)
    db.session.commit()

    login(client)

    response = client.get(
        f"/payment/start/{order.id}/upi",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/gateway/ui/" in response.headers["Location"]

    payment = PaymentGateway.query.filter_by(
        order_id=order.id
    ).first()

    assert payment is not None
    assert payment.status == "initiated"
    assert payment.method == "upi"


def test_gateway_generates_otp(client):
    user = create_user()

    order = Order(
        user_id=user.id,
        total_amount=250.0,
        status="pending_payment",
        payment_method="upi",
        payment_status="pending",
    )

    db.session.add(order)
    db.session.commit()

    payment = PaymentGateway(
        order_id=order.id,
        user_id=user.id,
        amount=250.0,
        method="upi",
        status="initiated",
    )

    db.session.add(payment)
    db.session.commit()

    login(client)

    response = client.get(
        f"/gateway/otp/{payment.id}",
    )

    assert response.status_code == 200

    refreshed_payment = db.session.get(
        PaymentGateway,
        payment.id,
    )

    assert refreshed_payment.status == "otp_sent"
    assert refreshed_payment.otp is not None
    assert re.fullmatch(r"\d{6}", refreshed_payment.otp)


def test_invalid_gateway_otp_fails_payment(client):
    user = create_user()

    order = Order(
        user_id=user.id,
        total_amount=250.0,
        status="pending_payment",
        payment_method="upi",
        payment_status="pending",
    )

    db.session.add(order)
    db.session.commit()

    payment = PaymentGateway(
        order_id=order.id,
        user_id=user.id,
        amount=250.0,
        method="upi",
        status="otp_sent",
        otp="123456",
    )

    db.session.add(payment)
    db.session.commit()

    login(client)

    response = client.post(
        f"/gateway/verify/{payment.id}",
        data={"otp": "000000"},
        follow_redirects=False,
    )

    assert response.status_code == 302

    refreshed_payment = db.session.get(
        PaymentGateway,
        payment.id,
    )

    assert refreshed_payment.status == "failed"


# ---------------------------------------------------------------------------
# Database / health
# ---------------------------------------------------------------------------

def test_database_is_available(app):
    from sqlalchemy import text

    with app.app_context():
        result = db.session.execute(
            text("SELECT 1")
        ).scalar()

        assert result == 1


def test_liveness(client):
    response = client.get("/health/live")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "ok"
    assert data["service"] == "maruti-pharmacy"


def test_readiness(client):
    response = client.get("/health/ready")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "ready"
    assert data["database"] == "ok"
