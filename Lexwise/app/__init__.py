from flask import Flask, jsonify, redirect, url_for
from flask_login import LoginManager
from flask_migrate import Migrate  # pyrefly: ignore
from dotenv import load_dotenv

from .config import Config
from .database.db import db

migrate = Migrate()
login_manager = LoginManager()


@login_manager.unauthorized_handler
def unauthorized():
    from flask import request
    if request.is_json or request.path.startswith(("/finance", "/ai", "/auth", "/subscriptions")):
        return jsonify({"error": "Unauthorized"}), 401
    return redirect("/")


def create_app(config_class=Config):
    load_dotenv()

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_class)

    # Initialise extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Import models so they are registered with SQLAlchemy
    from .models.user import User
    from .models.transaction import Transaction
    from .models.budget import Budget
    from .models.ai_profile import AIProfile
    from .models.goal import Goal
    from .models.investment import Investment

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    from .routes.auth_routes import auth_bp
    from .routes.finance_routes import finance_bp
    from .routes.ai_routes import ai_bp
    from .routes.subscription_routes import subscription_bp
    from .routes.frontend_routes import frontend_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(finance_bp, url_prefix="/finance")
    app.register_blueprint(ai_bp, url_prefix="/ai")
    app.register_blueprint(subscription_bp, url_prefix="/subscriptions")
    app.register_blueprint(frontend_bp)

    # Removed API index route to use frontend_bp

    # Create tables if they don't exist (dev convenience)
    with app.app_context():
        db.create_all()

    return app
