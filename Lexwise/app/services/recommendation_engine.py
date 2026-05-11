class RecommendationEngine:
    def suggest_categories(self, transactions):
        return ["Savings", "Investments", "Essentials"]

    def recommend_budget(self, user_profile):
        return {"recommended_budget": 0}
