import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


# Load environment variables
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "postgresql://test:test@localhost:5432/test")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    DEBUG = False
    MEDIA_FOLDER = os.path.join(os.getcwd(), os.environ.get("MEDIA_FOLDER", "uploads"))
    MEDIA_URL = "/uploads"
    MEDIA_DIR = "uploads"
    CORS_ALLOW_HEADERS = [
        "Content-Type",
        "Content-Length",
        "Accept-Encoding",
        "X-CSRF-Token",
        "Authorization",
        "accept",
        "origin",
        "Cache-Control",
        "X-Requested-With",
    ]
    CORS_EXPOSE_HEADERS = ["Content-Disposition", "Content-Type", "Content-Length"]
    CORS_SUPPORTS_CREDENTIALS = True
