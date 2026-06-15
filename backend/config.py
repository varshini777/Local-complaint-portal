import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv


load_dotenv()


class Config:
    BASE_DIR = Path(__file__).resolve().parent.parent

    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
    DEBUG = os.getenv("FLASK_ENV", "production").lower() == "development"

    # Use SQLite for development to avoid MySQL authentication issues
    if DEBUG:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'local_complaint.db'}"
    else:
        MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
        MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
        MYSQL_USER = os.getenv("MYSQL_USER", "root")
        MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
        MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "local_complaint_portal")

        _encoded_user = quote_plus(MYSQL_USER)
        _encoded_password = quote_plus(MYSQL_PASSWORD)
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{_encoded_user}:{_encoded_password}"
            f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = BASE_DIR / "backend" / "static" / "uploads"
    COMPLAINT_BEFORE_UPLOAD_FOLDER = (
        UPLOAD_FOLDER / "complaints" / "before"
    )
    COMPLAINT_AFTER_UPLOAD_FOLDER = (
        UPLOAD_FOLDER / "complaints" / "after"
    )
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

    ESCALATION_URGENT_DAYS = 3
    ESCALATION_CRITICAL_DAYS = 7

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    WTF_CSRF_ENABLED = False
