"""Tests for authentication routes."""


class TestRegister:

    def test_register_success(self, client):
        response = client.post("/auth/register", json={
            "name": "Alice",
            "email": "alice@example.com",
            "password": "securepass123"
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data["message"] == "User registered successfully"
        assert "user_id" in data

    def test_register_missing_field(self, client):
        response = client.post("/auth/register", json={
            "name": "Alice",
            "email": "alice@example.com"
            # missing password
        })
        assert response.status_code == 400
        assert "Missing" in response.get_json()["error"]

    def test_register_duplicate_email(self, client):
        client.post("/auth/register", json={
            "name": "Alice",
            "email": "dup@example.com",
            "password": "securepass123"
        })
        response = client.post("/auth/register", json={
            "name": "Bob",
            "email": "dup@example.com",
            "password": "securepass456"
        })
        assert response.status_code == 409

    def test_register_invalid_email(self, client):
        response = client.post("/auth/register", json={
            "name": "Alice",
            "email": "not-an-email",
            "password": "securepass123"
        })
        assert response.status_code == 400
        assert "email" in response.get_json()["error"].lower()

    def test_register_weak_password(self, client):
        response = client.post("/auth/register", json={
            "name": "Alice",
            "email": "alice2@example.com",
            "password": "short"
        })
        assert response.status_code == 400
        assert "8 characters" in response.get_json()["error"]

    def test_register_invalid_plan(self, client):
        response = client.post("/auth/register", json={
            "name": "Alice",
            "email": "alice3@example.com",
            "password": "securepass123",
            "plan": "enterprise"
        })
        assert response.status_code == 400

    def test_register_negative_income(self, client):
        response = client.post("/auth/register", json={
            "name": "Alice",
            "email": "alice4@example.com",
            "password": "securepass123",
            "monthly_income": -500
        })
        assert response.status_code == 400


class TestLogin:

    def test_login_success(self, client):
        client.post("/auth/register", json={
            "name": "Bob",
            "email": "bob@example.com",
            "password": "securepass123"
        })
        response = client.post("/auth/login", json={
            "email": "bob@example.com",
            "password": "securepass123"
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Login successful"
        assert data["user"]["email"] == "bob@example.com"

    def test_login_wrong_password(self, client):
        client.post("/auth/register", json={
            "name": "Bob",
            "email": "bob2@example.com",
            "password": "securepass123"
        })
        response = client.post("/auth/login", json={
            "email": "bob2@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post("/auth/login", json={
            "email": "nobody@example.com",
            "password": "anypassword1"
        })
        assert response.status_code == 401

    def test_login_missing_fields(self, client):
        response = client.post("/auth/login", json={
            "email": "bob@example.com"
        })
        assert response.status_code == 400


class TestProtectedRoutes:

    def test_me_requires_auth(self, client):
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_me_authenticated(self, authenticated_client):
        response = authenticated_client.get("/auth/me")
        assert response.status_code == 200
        data = response.get_json()
        assert data["email"] == "test@example.com"

    def test_logout(self, authenticated_client):
        response = authenticated_client.post("/auth/logout")
        assert response.status_code == 200

        # After logout, /me should return 401
        response = authenticated_client.get("/auth/me")
        assert response.status_code == 401
