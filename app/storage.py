
import mimetypes
import os
import uuid
from io import BytesIO

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import BotoCoreError, ClientError
from flask import current_app, url_for
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename


IMAGE_TYPES = {
    ".jpg": ("image/jpeg", "JPEG"),
    ".jpeg": ("image/jpeg", "JPEG"),
    ".png": ("image/png", "PNG"),
    ".webp": ("image/webp", "WEBP"),
    ".gif": ("image/gif", "GIF"),
}


class StorageError(Exception):
    """Safe, application-level error for product image storage."""


class StorageObjectNotFound(StorageError):
    """Raised when an image key does not exist in object storage."""


def _validate_image(upload):
    """Validate the file extension and actual image content."""
    safe_name = secure_filename(upload.filename or "")
    ext = os.path.splitext(safe_name)[1].lower()

    if not safe_name or ext not in IMAGE_TYPES:
        raise StorageError("Unsupported product image format.")

    expected_type, expected_format = IMAGE_TYPES[ext]

    try:
        upload.stream.seek(0)
        with Image.open(upload.stream) as image:
            if image.format != expected_format:
                raise StorageError(
                    "The image content does not match its file extension."
                )
            image.verify()

        upload.stream.seek(0)
        with Image.open(upload.stream) as image:
            image.load()

    except StorageError:
        raise
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise StorageError("Invalid or corrupted product image.") from exc
    finally:
        upload.stream.seek(0)

    return ext, expected_type


def get_s3_client():
    endpoint = current_app.config.get("S3_ENDPOINT_URL")
    access_key = current_app.config.get("S3_ACCESS_KEY")
    secret_key = current_app.config.get("S3_SECRET_KEY")

    if not endpoint or not access_key or not secret_key:
        raise StorageError(
            "Object storage is enabled but its configuration is incomplete."
        )

    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=current_app.config.get("S3_REGION", "us-east-1"),
        config=BotoConfig(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
        ),
    )


def upload_product_image(upload):
    """Save a validated product image locally or in private object storage."""
    ext, content_type = _validate_image(upload)
    object_name = f"{uuid.uuid4().hex}{ext}"

    if current_app.config.get("OBJECT_STORAGE_ENABLED", False):
        key = f"products/{object_name}"
        bucket = current_app.config.get("S3_BUCKET")

        if not bucket:
            raise StorageError("Object storage bucket is not configured.")

        try:
            upload.stream.seek(0)
            get_s3_client().put_object(
                Bucket=bucket,
                Key=key,
                Body=upload.stream,
                ContentType=content_type,
                CacheControl="private, max-age=3600",
            )
        except (BotoCoreError, ClientError, OSError) as exc:
            raise StorageError("Product image upload failed.") from exc

        return f"s3:{key}"

    folder = current_app.config.get("PRODUCT_IMAGE_UPLOAD_DIR")
    if not folder:
        folder = os.path.join(
            current_app.root_path, "static", "images", "products"
        )

    os.makedirs(folder, exist_ok=True)
    destination = os.path.join(folder, object_name)

    try:
        upload.stream.seek(0)
        upload.save(destination)
    except OSError as exc:
        raise StorageError("Local product image upload failed.") from exc

    return f"images/products/{object_name}"


def read_product_image(key):
    """Return image bytes and a validated image MIME type from object storage."""
    if not key.startswith("products/") or ".." in key.split("/") or "\\" in key:
        raise StorageError("Invalid product image key.")

    bucket = current_app.config.get("S3_BUCKET")
    if not bucket:
        raise StorageError("Object storage bucket is not configured.")

    try:
        response = get_s3_client().get_object(Bucket=bucket, Key=key)
        body = response["Body"].read()
    except ClientError as exc:
        code = str(exc.response.get("Error", {}).get("Code", ""))
        status = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode")

        if code in {"NoSuchKey", "NoSuchObject", "NotFound", "404"} or status == 404:
            raise StorageObjectNotFound("Product image not found.") from exc

        raise StorageError("Product image could not be retrieved.") from exc
    except (BotoCoreError, OSError, KeyError) as exc:
        raise StorageError("Product image could not be retrieved.") from exc

    ext = os.path.splitext(key)[1].lower()
    content_type, _ = IMAGE_TYPES.get(
        ext, ("application/octet-stream", None)
    )

    if response.get("ContentType") in {
        item[0] for item in IMAGE_TYPES.values()
    }:
        content_type = response["ContentType"]

    return BytesIO(body), content_type


def product_image_src(image_url):
    """Resolve legacy local paths and private S3 object keys to application URLs."""
    if not image_url:
        return url_for("static", filename="images/no-image.png")

    if image_url.startswith("s3:"):
        return url_for("media.product_image", key=image_url[3:])

    return url_for("static", filename=image_url)
