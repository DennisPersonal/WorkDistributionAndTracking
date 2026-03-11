import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///work_tracking.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Application
    APP_NAME = os.environ.get('APP_NAME', 'Work Distribution and Tracking')
    APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
    
    # Security
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    REMEMBER_COOKIE_SECURE = os.environ.get('REMEMBER_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    REMEMBER_COOKIE_HTTPONLY = os.environ.get('REMEMBER_COOKIE_HTTPONLY', 'True').lower() == 'true'
    
    # File upload
    MAX_CONTENT_LENGTH = int(eval(os.environ.get('MAX_CONTENT_LENGTH', '16 * 1024 * 1024')))  # 16MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'}
    
    # Feature flags
    ENABLE_REGISTRATION = os.environ.get('ENABLE_REGISTRATION', 'True').lower() == 'true'
    ENABLE_EMAIL_VERIFICATION = os.environ.get('ENABLE_EMAIL_VERIFICATION', 'False').lower() == 'true'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'
    SQLALCHEMY_ECHO = True  # Log SQL queries


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory database for tests
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Security settings for production
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    
    # Consider using PostgreSQL in production
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}