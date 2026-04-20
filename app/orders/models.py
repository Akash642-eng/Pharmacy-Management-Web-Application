from datetime import datetime
from app.extensions import db


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    address = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(15), nullable=True)

    total_amount = db.Column(db.Float, nullable=False)

    status = db.Column(db.String(30), default="pending_payment")

    payment_method = db.Column(db.String(20), nullable=True)
    payment_status = db.Column(db.String(20), default="pending")

    invoice_number = db.Column(db.String(50), unique=True, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="orders")

    items = db.relationship(
        "OrderItem",
        backref="order",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Order id={self.id} user_id={self.user_id} status={self.status}>"


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    product = db.relationship("Product")

    def __repr__(self):
        return f"<OrderItem order_id={self.order_id} product_id={self.product_id}>"
