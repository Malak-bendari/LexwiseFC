from flask import Blueprint, jsonify, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app.database.db import db
from app.models.user import User
from app.models.ai_profile import AIProfile

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    required_fields = ["name", "email", "password"]

    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            return jsonify({"error": f"Missing or empty field: {field}"}), 400

    email = data["email"].strip().lower()

    # Basic email validation
    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({"error": "Invalid email format"}), 400

    # Password strength check
    password = data["password"]
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({"error": "Email already exists"}), 409

    try:
        monthly_income = float(data.get("monthly_income", 0))
        if monthly_income < 0:
            return jsonify({"error": "Monthly income cannot be negative"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid monthly_income value"}), 400

    plan = data.get("plan", "go")
    if plan not in ["go", "premium"]:
        return jsonify({"error": "Invalid plan. Must be 'go' or 'premium'"}), 400

    user = User(
        name=data["name"].strip(),
        email=email,
        password_hash=generate_password_hash(data["password"]),
        monthly_income=monthly_income,
        plan=plan
    )

    try:
        db.session.add(user)
        db.session.commit()

        ai_profile = AIProfile(
            user_id=user.id,
            financial_goal=data.get("financial_goal"),
            risk_level=data.get("risk_level", "medium"),
            preferred_coaching_style=data.get("coaching_style", "balanced")
        )

        db.session.add(ai_profile)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Registration failed. Please try again."}), 500

    return jsonify({
        "message": "User registered successfully",
        "user_id": user.id
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    login_user(user)

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "plan": user.plan
        }
    })


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"})


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    return jsonify({
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "plan": current_user.plan,
        "monthly_income": current_user.monthly_income
    })