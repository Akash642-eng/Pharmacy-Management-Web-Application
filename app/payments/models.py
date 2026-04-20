from datetime import datetime
from app.extensions import db

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)

    method = db.Column(db.String(30), nullable=False)  # UPI / Card / COD
    status = db.Column(db.String(30), default="Success")
    amount = db.Column(db.Float, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship("Order")

    def __repr__(self):
        return f"<Payment order_id={self.order_id} method={self.method}>"
