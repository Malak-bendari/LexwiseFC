from flask import Blueprint, jsonify, request

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    return jsonify({"message": "Login endpoint", "data": data}), 200


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    return jsonify({"message": "Register endpoint", "data": data}), 201
