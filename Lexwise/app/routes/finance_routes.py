from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from app.database.db import db
from app.models.transaction import Transaction
from app.models.budget import Budget
from app.models.goal import Goal
from app.models.investment import Investment
from app.services.finance_service import FinanceService
from app.services.recommendation_engine import RecommendationEngine
from datetime import datetime

finance_bp = Blueprint("finance", __name__)


@finance_bp.route("/dashboard", methods=["GET"])
@login_required
def get_dashboard():
    user_id = current_user.id

    summary = FinanceService.calculate_monthly_summary(user_id)
    budget_status = FinanceService.analyze_budget_status(user_id)
    risks = FinanceService.detect_financial_risks(user_id)
    recommendations = RecommendationEngine.generate_recommendations(user_id)

    return jsonify({
        "summary": summary,
        "budgets": budget_status,
        "risks": risks,
        "recommendations": recommendations
    })


@finance_bp.route("/transactions", methods=["POST"])
@login_required
def create_transaction():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    required_fields = ["amount", "category", "transaction_type"]

    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            return jsonify({"error": f"Missing or empty field: {field}"}), 400

    try:
        amount = float(data["amount"])
        if amount <= 0:
            return jsonify({"error": "Amount must be positive"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid amount value"}), 400

    transaction_type = data["transaction_type"]
    if transaction_type not in ["income", "expense"]:
        return jsonify({"error": "transaction_type must be 'income' or 'expense'"}), 400

    transaction = Transaction(
        user_id=current_user.id,
        amount=amount,
        category=data["category"].strip(),
        description=(data.get("description") or "").strip() or None,
        transaction_type=transaction_type
    )

    try:
        db.session.add(transaction)
        db.session.commit()

        # Auto-update the matching budget's current_amount
        if transaction_type == "expense":
            month_key = FinanceService.get_month_key()
            budget = Budget.query.filter_by(
                user_id=current_user.id,
                category=transaction.category,
                month=month_key
            ).first()

            if budget:
                budget.current_amount += amount
                db.session.commit()

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to create transaction"}), 500

    return jsonify({
        "message": "Transaction created successfully",
        "transaction_id": transaction.id
    }), 201


@finance_bp.route("/transactions", methods=["GET"])
@login_required
def get_transactions():
    transactions = Transaction.query.filter_by(
        user_id=current_user.id
    ).order_by(Transaction.date.desc()).all()

    result = []

    for t in transactions:
        result.append({
            "id": t.id,
            "amount": t.amount,
            "category": t.category,
            "description": t.description,
            "transaction_type": t.transaction_type,
            "date": t.date.isoformat()
        })

    return jsonify(result)


@finance_bp.route("/budgets", methods=["POST"])
@login_required
def create_budget():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    required_fields = ["category", "limit_amount", "month"]

    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            return jsonify({"error": f"Missing or empty field: {field}"}), 400

    try:
        limit_amount = float(data["limit_amount"])
        if limit_amount <= 0:
            return jsonify({"error": "limit_amount must be positive"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid limit_amount value"}), 400

    try:
        current_amount = float(data.get("current_amount", 0))
        if current_amount < 0:
            return jsonify({"error": "current_amount cannot be negative"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid current_amount value"}), 400

    budget = Budget(
        user_id=current_user.id,
        category=data["category"].strip(),
        limit_amount=limit_amount,
        current_amount=current_amount,
        month=data["month"].strip()
    )

    try:
        db.session.add(budget)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to create budget"}), 500

    return jsonify({
        "message": "Budget created successfully",
        "budget_id": budget.id
    }), 201


@finance_bp.route("/budgets", methods=["GET"])
@login_required
def get_budgets():
    month = request.args.get("month", FinanceService.get_month_key())

    budgets = Budget.query.filter_by(
        user_id=current_user.id,
        month=month
    ).all()

    result = []
    for b in budgets:
        percentage = 0
        if b.limit_amount > 0:
            percentage = round((b.current_amount / b.limit_amount) * 100, 2)

        result.append({
            "id": b.id,
            "category": b.category,
            "limit_amount": b.limit_amount,
            "current_amount": b.current_amount,
            "percentage": percentage,
            "month": b.month
        })

    return jsonify(result)


@finance_bp.route("/goals", methods=["POST"])
@login_required
def create_goal():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    required_fields = ["name", "target_amount"]
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            return jsonify({"error": f"Missing or empty field: {field}"}), 400

    try:
        target_amount = float(data["target_amount"])
        if target_amount <= 0:
            return jsonify({"error": "target_amount must be positive"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid target_amount value"}), 400

    target_date = None
    if "target_date" in data and data["target_date"]:
        try:
            target_date = datetime.fromisoformat(data["target_date"].replace('Z', '+00:00'))
        except ValueError:
            pass # ignore invalid date format for now

    goal = Goal(
        user_id=current_user.id,
        name=data["name"].strip(),
        target_amount=target_amount,
        current_amount=float(data.get("current_amount", 0)),
        target_date=target_date
    )

    db.session.add(goal)
    db.session.commit()

    return jsonify({"message": "Goal created successfully", "goal_id": goal.id}), 201


@finance_bp.route("/goals", methods=["GET"])
@login_required
def get_goals():
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    result = []
    for g in goals:
        result.append({
            "id": g.id,
            "name": g.name,
            "target_amount": g.target_amount,
            "current_amount": g.current_amount,
            "target_date": g.target_date.isoformat() if g.target_date else None
        })
    return jsonify(result)


@finance_bp.route("/investments", methods=["POST"])
@login_required
def create_investment():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    required_fields = ["name", "asset_class", "amount_invested", "current_value"]
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            return jsonify({"error": f"Missing or empty field: {field}"}), 400

    try:
        amount_invested = float(data["amount_invested"])
        current_value = float(data["current_value"])
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid amounts"}), 400

    investment = Investment(
        user_id=current_user.id,
        name=data["name"].strip(),
        symbol=data.get("symbol", "").strip() or None,
        asset_class=data["asset_class"].strip(),
        amount_invested=amount_invested,
        current_value=current_value
    )

    db.session.add(investment)
    db.session.commit()

    return jsonify({"message": "Investment created successfully", "investment_id": investment.id}), 201


@finance_bp.route("/investments", methods=["GET"])
@login_required
def get_investments():
    investments = Investment.query.filter_by(user_id=current_user.id).all()
    result = []
    for i in investments:
        result.append({
            "id": i.id,
            "name": i.name,
            "symbol": i.symbol,
            "asset_class": i.asset_class,
            "amount_invested": i.amount_invested,
            "current_value": i.current_value
        })
    return jsonify(result)