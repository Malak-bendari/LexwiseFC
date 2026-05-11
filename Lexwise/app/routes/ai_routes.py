from flask import Blueprint, jsonify, request

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/profile", methods=["GET"])
def get_ai_profile():
    return jsonify({"message": "AI profile data"}), 200


@ai_bp.route("/suggestions", methods=["POST"])
def ai_suggestions():
    payload = request.json or {}
    return jsonify({"message": "AI suggestions", "payload": payload}), 200
