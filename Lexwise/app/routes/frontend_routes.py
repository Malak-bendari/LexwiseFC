from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from app.services.finance_service import FinanceService
from app.services.recommendation_engine import RecommendationEngine
from app.models.transaction import Transaction
from app.models.goal import Goal
from app.models.investment import Investment

frontend_bp = Blueprint("frontend", __name__)

@frontend_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("frontend.dashboard"))
    return redirect(url_for("frontend.login_page"))

@frontend_bp.route("/login")
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for("frontend.dashboard"))
    return render_template("login.html")

@frontend_bp.route("/dashboard")
@login_required
def dashboard():
    user_id = current_user.id
    summary = FinanceService.calculate_monthly_summary(user_id)
    budgets = FinanceService.analyze_budget_status(user_id)
    risks = FinanceService.detect_financial_risks(user_id)
    recommendations = RecommendationEngine.generate_recommendations(user_id)
    
    # Fetch all transactions
    all_transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).all()
    recent_transactions = all_transactions[:5] if all_transactions else []
    
    # Fetch goals and investments
    goals = Goal.query.filter_by(user_id=user_id).all()
    investments = Investment.query.filter_by(user_id=user_id).all()
    
    return render_template(
        "base.html", 
        user=current_user,
        summary=summary,
        budgets=budgets,
        risks=risks,
        recommendations=recommendations,
        recent_transactions=recent_transactions,
        all_transactions=all_transactions,
        goals=goals,
        investments=investments,
        force_fincoach=True
    )
