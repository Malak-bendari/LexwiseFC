from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from app.services.ai_service import AIService

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/coach", methods=["GET"])
@login_required
def get_ai_coach_message():
    result = AIService.generate_coach_message(current_user.id)
    return jsonify(result)


@ai_bp.route("/ask", methods=["POST"])
@login_required
def ask_ai_coach():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"error": "question is required"}), 400

    answer = AIService.answer_user_question(current_user.id, question)

    return jsonify(answer)