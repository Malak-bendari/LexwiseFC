from collections import defaultdict
from datetime import datetime, timezone

from app.models.transaction import Transaction
from app.models.budget import Budget


class FinanceService:

    @staticmethod
    def get_month_key(date=None):
        if date is None:
            date = datetime.now(timezone.utc)
        return date.strftime("%Y-%m")

    @staticmethod
    def calculate_monthly_summary(user_id):
        current_month = FinanceService.get_month_key()

        transactions = Transaction.query.filter(
            Transaction.user_id == user_id
        ).all()

        total_income = 0
        total_expenses = 0
        expenses_by_category = defaultdict(float)

        for transaction in transactions:
            transaction_month = transaction.date.strftime("%Y-%m")

            if transaction_month != current_month:
                continue

            if transaction.transaction_type == "income":
                total_income += transaction.amount
            else:
                total_expenses += transaction.amount
                expenses_by_category[transaction.category] += transaction.amount

        remaining = total_income - total_expenses

        savings_rate = 0
        if total_income > 0:
            savings_rate = round((remaining / total_income) * 100, 2)

        return {
            "month": current_month,
            "total_income": round(total_income, 2),
            "total_expenses": round(total_expenses, 2),
            "remaining": round(remaining, 2),
            "savings_rate": savings_rate,
            "expenses_by_category": dict(expenses_by_category)
        }

    @staticmethod
    def analyze_budget_status(user_id):
        current_month = FinanceService.get_month_key()

        budgets = Budget.query.filter_by(
            user_id=user_id,
            month=current_month
        ).all()

        result = []

        for budget in budgets:
            percentage = 0
            if budget.limit_amount > 0:
                percentage = round((budget.current_amount / budget.limit_amount) * 100, 2)

            status = "safe"

            if percentage >= 100:
                status = "exceeded"
            elif percentage >= 80:
                status = "warning"

            result.append({
                "category": budget.category,
                "limit_amount": budget.limit_amount,
                "current_amount": budget.current_amount,
                "percentage": percentage,
                "status": status
            })

        return result

    @staticmethod
    def detect_financial_risks(user_id):
        summary = FinanceService.calculate_monthly_summary(user_id)
        risks = []

        if summary["total_income"] == 0:
            risks.append({
                "level": "high",
                "message": "Aucun revenu détecté ce mois-ci."
            })

        if summary["savings_rate"] < 10 and summary["total_income"] > 0:
            risks.append({
                "level": "medium",
                "message": "Ton taux d'épargne est faible ce mois-ci."
            })

        for category, amount in summary["expenses_by_category"].items():
            if summary["total_expenses"] > 0:
                category_ratio = amount / summary["total_expenses"]

                if category_ratio > 0.4:
                    risks.append({
                        "level": "medium",
                        "message": f"La catégorie {category} représente plus de 40% de tes dépenses."
                    })

        return risks