from flask import Flask, jsonify
from flask_login import LoginManager
from flask_migrate import Migrate  # pyrefly: ignore
from dotenv import load_dotenv

from .config import Config
from .database.db import db

migrate = Migrate()
login_manager = LoginManager()


@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"error": "Authentication required"}), 401


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

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    from .routes.auth_routes import auth_bp
    from .routes.finance_routes import finance_bp
    from .routes.ai_routes import ai_bp
    from .routes.subscription_routes import subscription_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(finance_bp, url_prefix="/finance")
    app.register_blueprint(ai_bp, url_prefix="/ai")
    app.register_blueprint(subscription_bp, url_prefix="/subscriptions")

    # Root route — API index
    @app.route("/")
    def index():
        return jsonify({
            "name": "LexWise API",
            "version": "1.0.0",
            "description": "AI-powered financial coaching API",
            "endpoints": {
                "auth": {
                    "POST /auth/register": "Create a new account",
                    "POST /auth/login": "Log in",
                    "POST /auth/logout": "Log out",
                    "GET /auth/me": "Get current user info"
                },
                "finance": {
                    "GET /finance/dashboard": "Get financial dashboard",
                    "POST /finance/transactions": "Create a transaction",
                    "GET /finance/transactions": "List transactions",
                    "POST /finance/budgets": "Create a budget",
                    "GET /finance/budgets": "List budgets"
                },
                "ai": {
                    "GET /ai/coach": "Get AI coach message",
                    "POST /ai/ask": "Ask the AI coach a question"
                },
                "subscriptions": {
                    "GET /subscriptions/plan": "Get current plan",
                    "POST /subscriptions/upgrade": "Upgrade plan"
                }
            }
        })

    # Create tables if they don't exist (dev convenience)
    with app.app_context():
        db.create_all()

    return app
