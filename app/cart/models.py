from app.extensions import db
from datetime import datetime


class Cart(db.Model):
    __tablename__ = "carts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan"
    )

    def total_items(self):
        return sum(item.quantity for item in self.items)

    def total_amount(self):
        total = 0
        for item in self.items:
            if item.product:
                total += item.product.price * item.quantity
        return total


class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)

    cart_id = db.Column(
        db.Integer,
        db.ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )

    quantity = db.Column(db.Integer, nullable=False, default=1)

    cart = db.relationship(
        "Cart",
        back_populates="items"
    )

    product = db.relationship(
        "Product",
        back_populates="cart_items"
    )


    def item_total(self):
        if self.product:
            return self.product.price * self.quantity
        return 0
