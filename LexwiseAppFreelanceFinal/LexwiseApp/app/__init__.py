from flask import Flask, app, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from config import Config
import os
import logging
from logging.handlers import RotatingFileHandler

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
cors = CORS()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # ========== SECURITY HEADERS (NO HTTPS FORCE) ==========
    Talisman(app,
        content_security_policy={
            'default-src': "'self'",
            'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
            'script-src': ["'self'", "'unsafe-inline'"],
            'font-src': ["'self'", "https://fonts.gstatic.com"],
            'img-src': ["'self'", "data:"],
        },
        force_https=False,
        frame_options='DENY',
    )
    
    # ========== RATE LIMITING ==========
    limiter.init_app(app)
    
    # Session security
    app.config.update(
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=3600,
    )
    
    # ========== SECURITY HEADERS MIDDLEWARE ==========
    @app.after_request
    def add_security_headers(response):
        for key, value in Config.SECURITY_HEADERS.items():
            response.headers[key] = value
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        return response
    
    # ========== LOGGING ==========
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/lexwise.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    @app.before_request
    def log_request():
        app.logger.info(f'Request: {request.method} {request.path} from {request.remote_addr}')
    
    # Initialize other extensions
    db.init_app(app)
    login_manager.init_app(app)
    cors.init_app(app, supports_credentials=True)
    csrf.init_app(app)
    
    # ========== EXEMPT API ROUTES FROM CSRF ==========
    from app.routes.auth import auth_bp
    from app.routes.projects import projects_bp
    from app.routes.contracts import contracts_bp
    from app.routes.chat import chat_bp
    from app.routes.matches import matches_bp
    from app.routes.offers import offers_bp
    from app.routes.ai import ai_bp
    from app.routes.notifications import notifications_bp
    from app.routes.investors import investors_bp

# Register blueprint
    csrf.exempt(auth_bp)
    csrf.exempt(projects_bp)
    csrf.exempt(contracts_bp)
    csrf.exempt(chat_bp)
    csrf.exempt(matches_bp)
    csrf.exempt(offers_bp)
    csrf.exempt(ai_bp)
    csrf.exempt(notifications_bp)
    csrf.exempt(investors_bp)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to continue'
    login_manager.session_protection = 'strong'
    
    # ========== REGISTER BLUEPRINTS (ONLY ONCE!) ==========
    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(contracts_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(matches_bp)
    app.register_blueprint(offers_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(investors_bp)
    app.register_blueprint(ai_bp)
    
    # ========== FRONTEND ROUTES ==========
    @app.route('/')
    def index():
        return render_template('dashboard.html')
    
    @app.route('/<path:path>')
    def catch_all(path):
        return render_template('dashboard.html')
    
    # ========== CREATE DATABASE TABLES ==========
    with app.app_context():
        db.create_all()
        app.logger.info("Database created successfully")
        
        from app.models.user import User
        admin = User.query.filter_by(email='admin@lexwise.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@lexwise.com',
                profile_type='investor',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            app.logger.info("Admin user created")
    
    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))