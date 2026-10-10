import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MiB

    # Redis cache
    REDIS_URL = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0",
    )
    REDIS_CACHE_TTL_SECONDS = int(
        os.getenv("REDIS_CACHE_TTL_SECONDS", "60")
    )

    # S3-compatible object storage (disabled by default)
    OBJECT_STORAGE_ENABLED = (
        os.getenv("OBJECT_STORAGE_ENABLED", "false").lower()
        == "true"
    )
    S3_ENDPOINT_URL = os.getenv(
        "S3_ENDPOINT_URL",
        "http://127.0.0.1:9000",
    )
    S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
    S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
    S3_BUCKET = os.getenv(
        "S3_BUCKET",
        "maruti-pharmacy-products",
    )
    S3_REGION = os.getenv("S3_REGION", "us-east-1")

    # Email configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = (
        os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    )
    MAIL_USE_SSL = (
        os.getenv("MAIL_USE_SSL", "false").lower() == "true"
    )

    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    MAIL_DEFAULT_SENDER = (
        os.getenv("MAIL_DEFAULT_SENDER_NAME", "Maruti Pharmacy"),
        os.getenv("MAIL_USERNAME"),
    )