from flask import Blueprint, jsonify, request

subscription_bp = Blueprint("subscription", __name__)


@subscription_bp.route("/plans", methods=["GET"])
def get_plans():
    return jsonify({"message": "Subscription plans"}), 200


@subscription_bp.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.json or {}
    return jsonify({"message": "Subscribe endpoint", "data": data}), 200
