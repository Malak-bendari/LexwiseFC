"""Tests for AI coach routes."""


class TestAICoach:

    def test_coach_requires_auth(self, client):
        response = client.get("/ai/coach")
        assert response.status_code == 401

    def test_coach_message(self, authenticated_client):
        response = authenticated_client.get("/ai/coach")
        assert response.status_code == 200
        data = response.get_json()
        assert data["coach"] == "LexWise"
        assert "message" in data

    def test_ask_requires_auth(self, client):
        response = client.post("/ai/ask", json={
            "question": "Comment sont mes dépenses ?"
        })
        assert response.status_code == 401

    def test_ask_missing_question(self, authenticated_client):
        response = authenticated_client.post("/ai/ask", json={})
        assert response.status_code == 400

    def test_ask_about_expenses(self, authenticated_client):
        response = authenticated_client.post("/ai/ask", json={
            "question": "Quelles sont mes dépenses ?"
        })
        assert response.status_code == 200
        data = response.get_json()
        assert "answer" in data

    def test_ask_about_savings(self, authenticated_client):
        response = authenticated_client.post("/ai/ask", json={
            "question": "Quel est mon taux d'épargne ?"
        })
        assert response.status_code == 200
        data = response.get_json()
        assert "answer" in data

    def test_ask_about_budget(self, authenticated_client):
        response = authenticated_client.post("/ai/ask", json={
            "question": "Comment va mon budget ?"
        })
        assert response.status_code == 200
        data = response.get_json()
        assert "answer" in data

    def test_ask_general_question(self, authenticated_client):
        response = authenticated_client.post("/ai/ask", json={
            "question": "Donne-moi un conseil"
        })
        assert response.status_code == 200
        data = response.get_json()
        assert "answer" in data


class TestSubscription:

    def test_plan_requires_auth(self, client):
        response = client.get("/subscriptions/plan")
        assert response.status_code == 401

    def test_get_plan(self, authenticated_client):
        response = authenticated_client.get("/subscriptions/plan")
        assert response.status_code == 200
        data = response.get_json()
        assert "plan" in data
        assert "features" in data

    def test_upgrade_plan(self, authenticated_client):
        response = authenticated_client.post("/subscriptions/upgrade", json={
            "plan": "go"
        })
        assert response.status_code == 200

    def test_upgrade_invalid_plan(self, authenticated_client):
        response = authenticated_client.post("/subscriptions/upgrade", json={
            "plan": "enterprise"
        })
        assert response.status_code == 400
