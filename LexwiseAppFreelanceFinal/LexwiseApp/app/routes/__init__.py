# This file makes the routes directory a Python package
from app.routes.ai import ai_bp
from app.routes.auth import auth_bp
from app.routes.chat import chat_bp
from app.routes.contracts import contracts_bp
from app.routes.investors import investors_bp
from app.routes.main import bp as main_bp
from app.routes.matches import matches_bp
from app.routes.notifications import notifications_bp
from app.routes.offers import offers_bp
from app.routes.projects import projects_bp