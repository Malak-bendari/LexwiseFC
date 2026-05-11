import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change_this_secret")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///lexwise.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AI_API_KEY = os.environ.get("AI_API_KEY", "")
