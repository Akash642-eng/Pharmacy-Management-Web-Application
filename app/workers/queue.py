
from flask import current_app
from redis import Redis
from rq import Queue, Retry
from rq.job import JobStatus

from app.workers.email_tasks import send_order_confirmation


def enqueue_order_confirmation(order_id):
    """Queue an order confirmation with bounded retries and status-aware recovery."""
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

        job_id = f"order-confirmation-{order_id}"
        existing_job = queue.fetch_job(job_id)

        if existing_job is not None:
            status = existing_job.get_status()

            if status == JobStatus.FINISHED:
                current_app.logger.info(
                    "Order confirmation already processed: order_id=%s",
                    order_id,
                )
                return existing_job

            if status in (
                JobStatus.QUEUED,
                JobStatus.STARTED,
                JobStatus.DEFERRED,
                JobStatus.SCHEDULED,
                JobStatus.CREATED,
            ):
                current_app.logger.info(
                    "Order confirmation job already active: order_id=%s status=%s",
                    order_id,
                    status.value,
                )
                return existing_job

            # Only remove a terminal unsuccessful job before creating a
            # replacement. Do not delete jobs that may still be running.
            if status in (
                JobStatus.FAILED,
                JobStatus.STOPPED,
                JobStatus.CANCELED,
            ):
                existing_job.delete()

        return queue.enqueue(
            send_order_confirmation,
            order_id,
            job_id=job_id,
            job_timeout=120,
            result_ttl=86400,
            failure_ttl=604800,
            retry=Retry(max=3, interval=[10, 30, 60]),
        )
    finally:
        redis_connection.close()
