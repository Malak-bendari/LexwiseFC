class AIService:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def generate_insights(self, profile, transactions):
        return {"insights": [], "profile": profile}
