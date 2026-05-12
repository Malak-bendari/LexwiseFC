"""Tests for finance routes and services."""


class TestTransactions:

    def test_create_transaction_requires_auth(self, client):
        response = client.post("/finance/transactions", json={
            "amount": 50,
            "category": "food",
            "transaction_type": "expense"
        })
        assert response.status_code == 401

    def test_create_transaction_success(self, authenticated_client):
        response = authenticated_client.post("/finance/transactions", json={
            "amount": 50.00,
            "category": "food",
            "transaction_type": "expense",
            "description": "Lunch"
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data["message"] == "Transaction created successfully"
        assert "transaction_id" in data

    def test_create_income_transaction(self, authenticated_client):
        response = authenticated_client.post("/finance/transactions", json={
            "amount": 3000,
            "category": "salary",
            "transaction_type": "income"
        })
        assert response.status_code == 201

    def test_create_transaction_missing_fields(self, authenticated_client):
        response = authenticated_client.post("/finance/transactions", json={
            "amount": 50
            # missing category and transaction_type
        })
        assert response.status_code == 400

    def test_create_transaction_invalid_amount(self, authenticated_client):
        response = authenticated_client.post("/finance/transactions", json={
            "amount": "not-a-number",
            "category": "food",
            "transaction_type": "expense"
        })
        assert response.status_code == 400

    def test_create_transaction_negative_amount(self, authenticated_client):
        response = authenticated_client.post("/finance/transactions", json={
            "amount": -10,
            "category": "food",
            "transaction_type": "expense"
        })
        assert response.status_code == 400

    def test_create_transaction_invalid_type(self, authenticated_client):
        response = authenticated_client.post("/finance/transactions", json={
            "amount": 50,
            "category": "food",
            "transaction_type": "refund"
        })
        assert response.status_code == 400

    def test_get_transactions(self, authenticated_client):
        # Create some transactions
        authenticated_client.post("/finance/transactions", json={
            "amount": 100,
            "category": "salary",
            "transaction_type": "income"
        })
        authenticated_client.post("/finance/transactions", json={
            "amount": 30,
            "category": "food",
            "transaction_type": "expense"
        })

        response = authenticated_client.get("/finance/transactions")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) >= 2


class TestBudgets:

    def test_create_budget_requires_auth(self, client):
        response = client.post("/finance/budgets", json={
            "category": "food",
            "limit_amount": 500,
            "month": "2026-05"
        })
        assert response.status_code == 401

    def test_create_budget_success(self, authenticated_client):
        response = authenticated_client.post("/finance/budgets", json={
            "category": "food",
            "limit_amount": 500,
            "month": "2026-05"
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data["message"] == "Budget created successfully"

    def test_create_budget_missing_fields(self, authenticated_client):
        response = authenticated_client.post("/finance/budgets", json={
            "category": "food"
            # missing limit_amount and month
        })
        assert response.status_code == 400

    def test_get_budgets(self, authenticated_client):
        authenticated_client.post("/finance/budgets", json={
            "category": "food",
            "limit_amount": 500,
            "month": "2026-05"
        })

        response = authenticated_client.get("/finance/budgets?month=2026-05")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) >= 1


class TestDashboard:

    def test_dashboard_requires_auth(self, client):
        response = client.get("/finance/dashboard")
        assert response.status_code == 401

    def test_dashboard_success(self, authenticated_client):
        response = authenticated_client.get("/finance/dashboard")
        assert response.status_code == 200
        data = response.get_json()
        assert "summary" in data
        assert "budgets" in data
        assert "risks" in data
        assert "recommendations" in data


class TestBudgetAutoUpdate:

    def test_expense_updates_budget(self, authenticated_client):
        from app.services.finance_service import FinanceService
        current_month = FinanceService.get_month_key()

        # Create a budget for "food" this month
        authenticated_client.post("/finance/budgets", json={
            "category": "food",
            "limit_amount": 500,
            "month": current_month
        })

        # Create an expense in the "food" category
        authenticated_client.post("/finance/transactions", json={
            "amount": 75,
            "category": "food",
            "transaction_type": "expense"
        })

        # Check the budget was updated
        response = authenticated_client.get(f"/finance/budgets?month={current_month}")
        data = response.get_json()
        food_budget = [b for b in data if b["category"] == "food"][0]
        assert food_budget["current_amount"] == 75.0
