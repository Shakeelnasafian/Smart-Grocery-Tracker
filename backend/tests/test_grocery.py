"""Tests for grocery item CRUD endpoints."""

ITEM_PAYLOAD = {
    "name": "Milk",
    "quantity": "1L",
    "category": "Dairy",
    "expiry_date": "2026-04-01",
    "price": 2.99,
}


def test_create_grocery_item(client, auth_headers):
    response = client.post("/grocery/", json=ITEM_PAYLOAD, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Milk"
    assert data["category"] == "Dairy"
    assert data["price"] == 2.99


def test_get_grocery_items_empty(client, auth_headers):
    response = client.get("/grocery/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "pages" in data


def test_get_grocery_items_with_item(client, auth_headers):
    client.post("/grocery/", json=ITEM_PAYLOAD, headers=auth_headers)
    response = client.get("/grocery/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_search_grocery_items(client, auth_headers):
    client.post("/grocery/", json=ITEM_PAYLOAD, headers=auth_headers)
    response = client.get("/grocery/?search=Milk", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()["items"]
    assert any(i["name"] == "Milk" for i in items)


def test_filter_by_category(client, auth_headers):
    client.post("/grocery/", json=ITEM_PAYLOAD, headers=auth_headers)
    response = client.get("/grocery/?category=Dairy", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()["items"]
    assert all(i["category"] == "Dairy" for i in items)


def test_update_grocery_item(client, auth_headers):
    create_response = client.post("/grocery/", json=ITEM_PAYLOAD, headers=auth_headers)
    item_id = create_response.json()["id"]

    update_response = client.put(
        f"/grocery/{item_id}",
        json={"quantity": "2L", "price": 5.50},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["quantity"] == "2L"
    assert data["price"] == 5.50


def test_delete_grocery_item(client, auth_headers):
    create_response = client.post("/grocery/", json=ITEM_PAYLOAD, headers=auth_headers)
    item_id = create_response.json()["id"]

    delete_response = client.delete(f"/grocery/{item_id}", headers=auth_headers)
    assert delete_response.status_code == 200
    assert "deleted" in delete_response.json()["detail"].lower()


def test_delete_nonexistent_item(client, auth_headers):
    response = client.delete("/grocery/999999", headers=auth_headers)
    assert response.status_code == 404


def test_export_csv(client, auth_headers):
    client.post("/grocery/", json=ITEM_PAYLOAD, headers=auth_headers)
    response = client.get("/grocery/export/csv", headers=auth_headers)
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "Milk" in response.text
