"""Tests for analytics and budget endpoints."""
import pytest

ITEM = {"name": "Eggs", "quantity": "12", "category": "Dairy", "expiry_date": "2026-04-01", "price": 3.50}


def test_analytics_empty(client, auth_headers):
    response = client.get("/analytics/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_items" in data
    assert "expiry_stats" in data
    assert "category_breakdown" in data
    assert "monthly_spending" in data


def test_analytics_with_data(client, auth_headers):
    client.post("/grocery/", json=ITEM, headers=auth_headers)
    response = client.get("/analytics/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] >= 1


def test_create_budget(client, auth_headers):
    response = client.post(
        "/budget/",
        json={"month": 4, "year": 2026, "limit_amount": 300.0},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["limit_amount"] == 300.0
    assert data["month"] == 4


def test_get_budgets(client, auth_headers):
    client.post("/budget/", json={"month": 5, "year": 2026, "limit_amount": 250.0}, headers=auth_headers)
    response = client.get("/budget/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_duplicate_budget_rejected(client, auth_headers):
    client.post("/budget/", json={"month": 6, "year": 2026, "limit_amount": 200.0}, headers=auth_headers)
    response = client.post("/budget/", json={"month": 6, "year": 2026, "limit_amount": 300.0}, headers=auth_headers)
    assert response.status_code == 400


def test_shopping_list(client, auth_headers):
    response = client.get("/shopping/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_add_shopping_item(client, auth_headers):
    response = client.post(
        "/shopping/",
        json={"name": "Bread", "quantity": "1 loaf", "category": "Bakery"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Bread"


def test_mark_shopping_item_purchased(client, auth_headers):
    create = client.post(
        "/shopping/",
        json={"name": "Butter", "quantity": "250g", "category": "Dairy"},
        headers=auth_headers,
    )
    item_id = create.json()["id"]
    update = client.put(f"/shopping/{item_id}", json={"is_purchased": True}, headers=auth_headers)
    assert update.status_code == 200
    assert update.json()["is_purchased"] is True


def test_expiring_items_endpoint(client, auth_headers):
    response = client.get("/alerts/expiring?days=30", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "count" in data
