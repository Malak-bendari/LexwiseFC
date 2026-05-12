from app.services.finance_service import FinanceService


class RecommendationEngine:

    @staticmethod
    def generate_recommendations(user_id):
        summary = FinanceService.calculate_monthly_summary(user_id)
        risks = FinanceService.detect_financial_risks(user_id)

        recommendations = []

        if summary["total_income"] == 0:
            recommendations.append({
                "type": "income",
                "priority": "high",
                "title": "Ajoute tes revenus",
                "message": "Pour obtenir une analyse fiable, commence par enregistrer tes revenus mensuels."
            })

        if summary["savings_rate"] < 10 and summary["total_income"] > 0:
            recommendations.append({
                "type": "saving",
                "priority": "high",
                "title": "Augmente ton taux d'épargne",
                "message": "Essaie de viser au moins 10% d'épargne ce mois-ci."
            })

        expenses_by_category = summary["expenses_by_category"]

        if expenses_by_category:
            highest_category = max(expenses_by_category, key=expenses_by_category.get)
            highest_amount = expenses_by_category[highest_category]

            recommendations.append({
                "type": "spending",
                "priority": "medium",
                "title": f"Surveille tes dépenses en {highest_category}",
                "message": f"Ta plus grosse catégorie de dépense est {highest_category} avec {highest_amount}."
            })

        if not risks and summary["total_income"] > 0:
            recommendations.append({
                "type": "positive",
                "priority": "low",
                "title": "Bonne gestion financière",
                "message": "Ton budget semble stable pour le moment. Continue comme ça."
            })

        return recommendations