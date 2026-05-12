import pytest
from app import create_app
from app.database.db import db as _db


@pytest.fixture(scope="session")
def app():
    """Create the Flask application for testing."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",
    })

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    """Provide a clean database for each test."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture(scope="function")
def client(app, db):
    """Provide a test client."""
    return app.test_client()


@pytest.fixture(scope="function")
def authenticated_client(client):
    """Provide a test client with a logged-in user."""
    # Register a user
    client.post("/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "monthly_income": 3000,
        "plan": "premium"
    })

    # Login
    client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })

    return client
