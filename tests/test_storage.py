
from io import BytesIO

import pytest
from PIL import Image
from werkzeug.datastructures import FileStorage

from app import create_app
from app import storage


@pytest.fixture
def storage_app(tmp_path):
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "OBJECT_STORAGE_ENABLED": False,
        "PRODUCT_IMAGE_UPLOAD_DIR": str(tmp_path),
        "S3_ENDPOINT_URL": "http://127.0.0.1:9000",
        "S3_ACCESS_KEY": "test-access",
        "S3_SECRET_KEY": "test-secret",
        "S3_BUCKET": "maruti-pharmacy-products",
        "MAX_CONTENT_LENGTH": 10 * 1024 * 1024,
    })
    return app


def make_image_bytes(image_format="JPEG"):
    """Create a valid image in memory for upload tests."""
    image = Image.new("RGB", (2, 2), color="white")
    stream = BytesIO()
    image.save(stream, format=image_format)
    return stream.getvalue()


def make_upload(filename="medicine.jpg", content=None):
    """Build a multipart-style file upload with valid image content."""
    if content is None:
        content = make_image_bytes()

    return FileStorage(
        stream=BytesIO(content),
        filename=filename,
        content_type="image/jpeg",
    )


def test_local_upload_saves_image(storage_app, tmp_path):
    image_bytes = make_image_bytes()

    with storage_app.app_context():
        image_url = storage.upload_product_image(
            make_upload(content=image_bytes)
        )

    assert image_url.startswith("images/products/")

    saved_file = tmp_path / image_url.split("/")[-1]
    assert saved_file.is_file()
    assert saved_file.read_bytes() == image_bytes


def test_unsupported_extension_is_rejected(storage_app):
    with storage_app.app_context():
        with pytest.raises(storage.StorageError):
            storage.upload_product_image(make_upload("payload.exe"))


def test_corrupted_image_is_rejected(storage_app):
    with storage_app.app_context():
        with pytest.raises(storage.StorageError):
            storage.upload_product_image(
                make_upload(content=b"this is not a real image")
            )


def test_mismatched_extension_is_rejected(storage_app):
    png_bytes = make_image_bytes("PNG")

    with storage_app.app_context():
        with pytest.raises(storage.StorageError):
            storage.upload_product_image(
                make_upload("medicine.jpg", png_bytes)
            )


def test_s3_upload_uses_private_bucket(storage_app, monkeypatch):
    class FakeS3:
        def __init__(self):
            self.uploaded = None

        def put_object(self, **kwargs):
            self.uploaded = kwargs

    image_bytes = make_image_bytes()
    fake = FakeS3()

    monkeypatch.setattr(storage, "get_s3_client", lambda: fake)
    storage_app.config["OBJECT_STORAGE_ENABLED"] = True

    with storage_app.app_context():
        image_url = storage.upload_product_image(
            make_upload(content=image_bytes)
        )

    assert image_url.startswith("s3:products/")
    assert fake.uploaded["Bucket"] == "maruti-pharmacy-products"
    assert fake.uploaded["Key"] == image_url[3:]
    assert fake.uploaded["ContentType"] == "image/jpeg"
    assert fake.uploaded["Body"].read() == image_bytes
    assert fake.uploaded["CacheControl"] == "private, max-age=3600"


def test_private_image_can_be_served_through_media_endpoint(
    storage_app, monkeypatch
):
    image_bytes = make_image_bytes()

    class FakeS3:
        def get_object(self, **kwargs):
            assert kwargs["Bucket"] == "maruti-pharmacy-products"
            assert kwargs["Key"] == "products/example.jpg"

            return {
                "Body": BytesIO(image_bytes),
                "ContentType": "image/jpeg",
            }

    monkeypatch.setattr(storage, "get_s3_client", lambda: FakeS3())

    # Enable object storage for this endpoint test.
    storage_app.config["OBJECT_STORAGE_ENABLED"] = True
    client = storage_app.test_client()

    response = client.get("/media/products/example.jpg")

    assert response.status_code == 200
    assert response.data == image_bytes
    assert response.mimetype == "image/jpeg"
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_media_endpoint_rejects_invalid_object_key(storage_app):
    storage_app.config["OBJECT_STORAGE_ENABLED"] = True
    client = storage_app.test_client()

    response = client.get("/media/other/example.jpg")

    assert response.status_code == 503


def test_missing_image_uses_placeholder(storage_app):
    with storage_app.test_request_context():
        image_url = storage.product_image_src(None)

    assert image_url.endswith("/static/images/no-image.png")
