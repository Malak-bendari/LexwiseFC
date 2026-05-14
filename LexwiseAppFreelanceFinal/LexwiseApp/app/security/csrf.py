from flask_wtf.csrf import CSRFProtect
from flask import request, jsonify

csrf = CSRFProtect()

def init_csrf(app):
    """Initialize CSRF protection for the app"""
    csrf.init_app(app)
    
    # Exempt API routes from CSRF if using token-based auth
    @app.after_request
    def set_csrf_cookie(response):
        response.set_cookie('csrf_token', csrf._get_csrf_token())
        return response

def get_csrf_token():
    """Get CSRF token for forms"""
    return csrf._get_csrf_token()

def protect_route(route_function):
    """Decorator to protect routes with CSRF"""
    from functools import wraps
    
    @wraps(route_function)
    def decorated_function(*args, **kwargs):
        # Skip CSRF check for GET, HEAD, OPTIONS, TRACE
        if request.method in ['GET', 'HEAD', 'OPTIONS', 'TRACE']:
            return route_function(*args, **kwargs)
        
        # For API routes using bearer token, skip CSRF
        if request.headers.get('Authorization'):
            return route_function(*args, **kwargs)
        
        # For form submissions, CSRF is handled by Flask-WTF
        return route_function(*args, **kwargs)
    
    return decorated_function