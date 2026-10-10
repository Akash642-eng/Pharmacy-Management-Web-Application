from redis import Redis
from rq import Queue
from flask import current_app

from app.workers.email_tasks import send_order_confirmation


def enqueue_order_confirmation(order_id):
    redis_connection = Redis.from_url(
        current_app.config["REDIS_URL"],
        socket_connect_timeout=2,
        socket_timeout=2,
    )

    try:
        queue = Queue(
            "emails",
            connection=redis_connection,
            default_timeout=120,
        )

        return queue.enqueue(
            send_order_confirmation,
            order_id,
            job_timeout=120,
            result_ttl=86400,
            failure_ttl=604800,
        )
    finally:
        redis_connection.close()
