from flask import Blueprint, jsonify, request

finance_bp = Blueprint("finance", __name__)


@finance_bp.route("/transactions", methods=["GET"])
def get_transactions():
    return jsonify({"message": "List transactions"}), 200


@finance_bp.route("/budgets", methods=["GET"])
def get_budgets():
    return jsonify({"message": "List budgets"}), 200
