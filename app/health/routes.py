from flask import Blueprint, jsonify
from sqlalchemy import text

from app.extensions import db


health_bp = Blueprint(
    "health",
    __name__,
    url_prefix="/health",
)


@health_bp.get("/live")
def liveness():
    return jsonify(
        status="ok",
        service="maruti-pharmacy",
    ), 200


@health_bp.get("/ready")
def readiness():
    try:
        db.session.execute(text("SELECT 1"))

        return jsonify(
            status="ready",
            database="ok",
        ), 200

    except Exception:
        db.session.rollback()

        return jsonify(
            status="not_ready",
            database="unavailable",
        ), 503
