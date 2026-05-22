"""
Configuration management for Hybi Books application.
Loads settings from environment variables with sensible defaults.
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.absolute()

# Database
DB_PATH = BASE_DIR / "books.db"

# Flask Configuration
class Config:
    """Base configuration class."""
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database (legacy sqlite path for raw SQL helpers)
    DATABASE = str(DB_PATH)
    # SQLAlchemy ORM configuration (used for e-commerce features)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CSRF Protection
    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'True').lower() == 'true'
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    
    # Email Configuration
    SMTP_HOST = os.environ.get('SMTP_HOST')
    SMTP_PORT = int(os.environ.get('SMTP_PORT') or 25)
    SMTP_USER = os.environ.get('SMTP_USER')
    SMTP_PASS = os.environ.get('SMTP_PASS')
    FROM_EMAIL = os.environ.get('FROM_EMAIL') or 'noreply@chamsach.vn'
    
    # reCAPTCHA
    RECAPTCHA_SECRET = os.environ.get('RECAPTCHA_SECRET')
    RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY')
    
    # File Uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'
    AVATAR_FOLDER = BASE_DIR / 'static' / 'avatars'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Caching
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # Pagination
    BOOKS_PER_PAGE = 9
    REVIEWS_PER_PAGE = 10

    # E-commerce: shipping
    SHIPPING_FEE = 30000  # 30k VND
    FREE_SHIP_THRESHOLD = 300000  # free ship if subtotal > 300k
    
    # Application
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    CACHE_TYPE = 'null'  # Disable caching in development
    # Disable CSRF in development for easier testing (enable in production!)
    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'False').lower() == 'true'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATABASE = str(BASE_DIR / 'test.db')
    CACHE_TYPE = 'null'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on FLASK_ENV environment variable."""
    env = os.environ.get('FLASK_ENV', 'development')
    config_class = config.get(env, config['default'])
    
    # Require SECRET_KEY in production
    if config_class == ProductionConfig and not os.environ.get('SECRET_KEY'):
        raise ValueError(
            "SECRET_KEY environment variable must be set in production! "
            "Set FLASK_ENV=development for development mode, or set SECRET_KEY in .env file."
        )
    
    return config_class

