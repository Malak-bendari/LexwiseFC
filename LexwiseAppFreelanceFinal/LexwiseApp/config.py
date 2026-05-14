import os
import secrets
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ========== SECRET KEYS ==========
    # NEVER commit real keys to git!
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        if os.environ.get('FLASK_ENV') == 'production':
            raise ValueError("SECRET_KEY must be set in production!")
        SECRET_KEY = secrets.token_urlsafe(32)
    
    WTF_CSRF_SECRET_KEY = os.environ.get('CSRF_SECRET_KEY', secrets.token_urlsafe(32))
    
    # ========== ENVIRONMENT ==========
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'
    
    # ========== DATABASE ==========
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    INSTANCE_PATH = os.path.join(BASE_DIR, 'instance')
    DATABASE_PATH = os.path.join(INSTANCE_PATH, 'lexwise.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # ========== SESSION SECURITY ==========
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = 3600
    
    # ========== CSRF ==========
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    WTF_CSRF_SSL_STRICT = True if SESSION_COOKIE_SECURE else False
    
    # ========== FILE UPLOAD ==========
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}
    
    # ========== RATE LIMITING ==========
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', "memory://")
    RATELIMIT_STRATEGY = "fixed-window"
    RATELIMIT_HEADERS_ENABLED = True
    
    # ========== SECURITY HEADERS ==========
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
    }
    
    # ========== API KEYS ==========
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    
    # Create folders
    os.makedirs(INSTANCE_PATH, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)