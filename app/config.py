import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False

MAIL_USERNAME = "speedyy6789@gmail.com"
MAIL_PASSWORD = "<REDACTED>"

MAIL_DEFAULT_SENDER = ("Maruti Pharmacy", "speedyy6789@gmail.com")
