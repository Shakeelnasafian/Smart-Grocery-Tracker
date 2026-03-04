"""Tests for authentication endpoints."""
import pytest


def test_register_new_user(client):
    response = client.post("/register", json={"email": "newuser@example.com", "password": "securepass123"})
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client, test_user):
    response = client.post("/register", json={"email": "test@example.com", "password": "anypassword"})
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success(client, test_user):
    response = client.post("/token", data={"username": "test@example.com", "password": "testpassword123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    response = client.post("/token", data={"username": "test@example.com", "password": "wrongpassword"})
    assert response.status_code == 400
    assert "Invalid credentials" in response.json()["detail"]


def test_login_unknown_user(client):
    response = client.post("/token", data={"username": "nobody@example.com", "password": "pass"})
    assert response.status_code == 400


def test_get_me(client, auth_headers):
    response = client.get("/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_logout_and_token_revoked(client, auth_headers):
    # Logout
    response = client.post("/logout", headers=auth_headers)
    assert response.status_code == 200

    # Subsequent request with same token should fail
    response = client.get("/me", headers=auth_headers)
    assert response.status_code == 401


def test_access_protected_route_without_token(client):
    response = client.get("/grocery/")
    assert response.status_code == 401
