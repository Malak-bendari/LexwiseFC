import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY or SECRET_KEY == "change_this_secret":
        raise ValueError("No valid SECRET_KEY set for Flask application.")
        
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///lexwise.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

    # Session cookie security (A05)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # SESSION_COOKIE_SECURE = True  # Commented out for local development (requires HTTPS)
