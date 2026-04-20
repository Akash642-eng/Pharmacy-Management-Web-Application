from datetime import datetime, date
from app.extensions import db


class Product(db.Model):
    __tablename__ = "products" 

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)


    is_offer = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    batch_number = db.Column(db.String(100), nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    reorder_level = db.Column(db.Integer, default=10)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


    cart_items = db.relationship(
        "CartItem",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    def is_low_stock(self):
        return self.stock <= (self.reorder_level or 0)

    def is_expired(self):
        if not self.expiry_date:
            return False
        return self.expiry_date < date.today()

    def __repr__(self):
        return f"<Product {self.id} - {self.name}>"

    def is_low_stock(self):
        if self.reorder_level is None:
            return False
        return self.stock <= self.reorder_level
