from datetime import datetime
from app.extensions import db


class PaymentGateway(db.Model):
    __tablename__ = "payment_gateway"

    id = db.Column(db.Integer, primary_key=True)


    order_id = db.Column(db.Integer, nullable=False, index=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)

    amount = db.Column(db.Float, nullable=False)
    method = db.Column(
        db.String(20),
        nullable=False
    ) 

    status = db.Column(
        db.String(20),
        nullable=False,
        default="initiated"
    )

    otp = db.Column(db.String(6), nullable=True)
    otp_attempts = db.Column(db.Integer, default=0)
    otp_verified_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return (
            f"<PaymentGateway id={self.id} "
            f"order_id={self.order_id} "
            f"method={self.method} "
            f"status={self.status}>"
        )
