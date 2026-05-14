from flask import Blueprint, render_template, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.models.reset_token import PasswordResetToken
from app.security.sanitizers import sanitize_input, validate_email
from flask import session as flask_session
import re
import secrets
from datetime import datetime, timedelta

# Create blueprint FIRST
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# ========== PASSWORD VALIDATION ==========
def validate_password_strength(password):
    """Check password strength against security requirements"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character (!@#$%^&* etc.)")
    
    return errors

# ========== REGISTER ==========
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = sanitize_input(data.get('username', ''))[:50]
    email = sanitize_input(data.get('email', ''))[:100]
    password = data.get('password', '')
    profile_type = data.get('profile_type', 'freelancer')
    
    # Validation
    if not username or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400
    
    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
    
    if not validate_email(email):
        return jsonify({'error': 'Invalid email address'}), 400
    
    # Check password strength
    password_errors = validate_password_strength(password)
    if password_errors:
        return jsonify({'error': password_errors[0]}), 400
    
    if profile_type not in ['freelancer', 'investor']:
        return jsonify({'error': 'Invalid profile type'}), 400
    
    # Check existing users
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 400
    
    # Create user with hashed password
    user = User(username=username, email=email, profile_type=profile_type)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    login_user(user)
    
    return jsonify({
        'success': True,
        'user': user.to_dict(),
        'message': 'Registration successful!'
    })

# ========== LOGIN ==========
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = sanitize_input(data.get('email', ''))[:100]
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        login_user(user)
        return jsonify({'success': True, 'user': user.to_dict()})
    
    return jsonify({'error': 'Invalid email or password'}), 401

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

# ========== GET CURRENT USER ==========
@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({'user': current_user.to_dict()})

# ========== UPDATE PROFILE ==========
@auth_bp.route('/update-profile', methods=['PUT'])
@login_required
def update_profile():
    data = request.get_json()
    username = sanitize_input(data.get('username', ''))[:50]
    
    if username and len(username) >= 3:
        existing = User.query.filter_by(username=username).first()
        if existing and existing.id != current_user.id:
            return jsonify({'error': 'Username already taken'}), 400
        current_user.username = username
    
    db.session.commit()
    return jsonify({'success': True, 'user': current_user.to_dict()})

# ========== CHANGE PASSWORD ==========
@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Current and new password required'}), 400
    
    if new_password != confirm_password:
        return jsonify({'error': 'New passwords do not match'}), 400
    
    # Verify current password
    if not current_user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Validate new password strength
    password_errors = validate_password_strength(new_password)
    if password_errors:
        return jsonify({'error': password_errors[0]}), 400
    
    # Update password
    current_user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Password changed successfully!'})

# ========== FORGOT PASSWORD ==========
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = sanitize_input(data.get('email', ''))[:100]
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    # For security, always return success even if email doesn't exist
    if not user:
        return jsonify({
            'success': True,
            'message': 'If an account exists, a reset link has been sent.'
        })
    
    # Delete old unused tokens
    PasswordResetToken.query.filter_by(user_id=user.id, used=False).delete()
    
    # Generate new token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at,
        used=False
    )
    db.session.add(reset_token)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'If an account exists, a reset link has been sent to your email.',
        'debug_token': token  # Remove in production, helpful for testing
    })

# ========== RESET PASSWORD ==========
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')
    
    if not token or not new_password:
        return jsonify({'error': 'Token and new password required'}), 400
    
    if new_password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400
    
    reset_token = PasswordResetToken.query.filter_by(token=token, used=False).first()
    
    if not reset_token:
        return jsonify({'error': 'Invalid or expired token'}), 400
    
    if reset_token.expires_at < datetime.utcnow():
        return jsonify({'error': 'Token has expired'}), 400
    
    user = User.query.get(reset_token.user_id)
    user.set_password(new_password)
    reset_token.used = True
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Password reset successfully!'})

# ========== CHECK SESSION ==========
@auth_bp.route('/check-session', methods=['GET'])
def check_session():
    return jsonify({
        'authenticated': current_user.is_authenticated,
        'user_id': current_user.id if current_user.is_authenticated else None,
        'session_cookie_exists': request.cookies.get('session') is not None
    })