import io
from pathlib import Path
from werkzeug.datastructures import FileStorage
from app import create_app
from app.storage import upload_product_image, read_product_image

app = create_app()

with app.app_context():
    path = Path("/app/app/static/images/products/diabetes-strip.jpg")
    if not path.exists():
        raise SystemExit(f"Test image not found: {path}")

    with path.open("rb") as f:
        source = f.read()

    upload = FileStorage(
        stream=io.BytesIO(source),
        filename="diabetes-strip.jpg",
        content_type="image/jpeg",
    )

    reference = upload_product_image(upload)
    print("S3 reference generated:", reference.startswith("s3:"))

    key = reference[3:]
    stream, content_type = read_product_image(key)
    retrieved = stream.read()
    stream.close()

    print("Retrieval:", "SUCCESS" if retrieved else "FAILED")
    print("Content type:", content_type)
    print("Retrieved bytes:", len(retrieved))
    print("Source matches:", retrieved == source)
    print("Temporary key:", key)
