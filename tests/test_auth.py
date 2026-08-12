import pytest

from app import create_app
from app.extensions import db


@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, SQLALCHEMY_DATABASE_URI="sqlite://")
    with app.app_context():
        db.drop_all()
        db.create_all()
    yield app.test_client()
    with app.app_context():
        db.drop_all()


def test_register_and_login(client):
    response = client.post(
        "/register",
        data={
            "username": "survivor",
            "email": "survivor@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Welcome to Prompt2Play" in response.data

    login_response = client.post(
        "/login",
        data={
            "email": "survivor@example.com",
            "password": "password123",
        },
        follow_redirects=True,
    )
    assert login_response.status_code == 200
    assert b"Welcome back!" in login_response.data


def test_dashboard_requires_login(client):
    response = client.get("/dashboard")
    assert response.status_code == 302
