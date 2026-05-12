from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from app.database.db import db
from app.models.user import User

subscription_bp = Blueprint("subscription", __name__)


@subscription_bp.route("/plan", methods=["GET"])
@login_required
def get_user_plan():
    return jsonify({
        "user_id": current_user.id,
        "plan": current_user.plan,
        "features": get_plan_features(current_user.plan)
    })


@subscription_bp.route("/upgrade", methods=["POST"])
@login_required
def upgrade_plan():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    new_plan = data.get("plan")

    if new_plan not in ["go", "premium"]:
        return jsonify({"error": "Invalid plan. Must be 'go' or 'premium'"}), 400

    if current_user.plan == new_plan:
        return jsonify({"message": f"Already on the '{new_plan}' plan"}), 200

    try:
        current_user.plan = new_plan
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to update plan"}), 500

    return jsonify({
        "message": "Plan updated successfully",
        "plan": current_user.plan
    })


def get_plan_features(plan):
    if plan == "premium":
        return [
            "AI financial coach",
            "Personalized recommendations",
            "Advanced insights",
            "Goal tracking",
            "Financial health score"
        ]

    return [
        "Basic dashboard",
        "Transactions tracking",
        "Simple budget overview"
    ]