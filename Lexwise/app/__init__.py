from flask import Flask
from .config import Config
from .routes.auth_routes import auth_bp
from .routes.finance_routes import finance_bp
from .routes.ai_routes import ai_bp
from .routes.subscription_routes import subscription_bp


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_class)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(finance_bp, url_prefix="/finance")
    app.register_blueprint(ai_bp, url_prefix="/ai")
    app.register_blueprint(subscription_bp, url_prefix="/subscriptions")

    return app
