import os
from datetime import timedelta


class Config:
    """Base configuration class."""

    # Database configuration
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or "sqlite:///credit_cards.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # Security configuration
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your-secret-key-here"
    WTF_CSRF_ENABLED = True

    # File upload configuration
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER") or "static/uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Allowed file extensions for uploads
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    TESTING = False
    # For local development, you can use either SQLite or PostgreSQL
    # To use PostgreSQL locally, set DATABASE_URL environment variable:
    # export DATABASE_URL="postgresql://username:password@localhost/credit_cards_dev"


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    UPLOAD_FOLDER = "/tmp/test_uploads"


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    TESTING = False

    # Use more secure settings in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

    # PostgreSQL-specific production settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 10,
        "max_overflow": 20,
    }


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
