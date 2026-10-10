
from flask import Blueprint, abort, current_app, send_file

from app.storage import StorageError, StorageObjectNotFound, read_product_image


media_bp = Blueprint("media", __name__, url_prefix="/media")


@media_bp.get("/<path:key>")
def product_image(key):
    try:
        image_stream, content_type = read_product_image(key)
    except StorageObjectNotFound:
        abort(404)
    except StorageError:
        current_app.logger.exception("Unable to retrieve product image")
        abort(503)

    response = send_file(
        image_stream,
        mimetype=content_type,
        download_name=key.rsplit("/", 1)[-1],
        max_age=3600,
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response
