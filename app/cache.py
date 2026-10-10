import json

from flask import current_app


def _cache_key():
    return "products:catalog:v1"


def get_cached_product_catalog():
    client = current_app.extensions.get("redis_client")

    if client is None:
        return None

    try:
        value = client.get(_cache_key())

        if value is None:
            return None

        return json.loads(value)

    except Exception:
        current_app.logger.warning(
            "Redis catalogue cache read failed; using database",
            exc_info=True,
        )
        return None


def set_cached_product_catalog(products):
    client = current_app.extensions.get("redis_client")

    if client is None:
        return

    try:
        client.set(
            _cache_key(),
            json.dumps(products),
            ex=current_app.config["REDIS_CACHE_TTL_SECONDS"],
        )

    except Exception:
        current_app.logger.warning(
            "Redis catalogue cache write failed",
            exc_info=True,
        )


def invalidate_product_catalog():
    client = current_app.extensions.get("redis_client")

    if client is None:
        return

    try:
        client.delete(_cache_key())

    except Exception:
        current_app.logger.warning(
            "Redis catalogue cache invalidation failed",
            exc_info=True,
        )