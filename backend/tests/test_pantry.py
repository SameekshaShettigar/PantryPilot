from uuid import uuid4


def test_pantry_crud_operations(client):
    """
    Tests authenticated Pantry CRUD endpoints (POST /pantry, GET /pantry).
    """
    unique_user = f"pantryuser_{uuid4().hex[:6]}"
    email = f"{unique_user}@example.com"
    password = "TestPassword123!"

    # Register & Login
    client.post("/auth/register", json={"username": unique_user, "email": email, "password": password})
    login_res = client.post("/auth/login", data={"username": unique_user, "password": password})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Add Pantry Item
    add_res = client.post(
        "/pantry",
        headers=headers,
        json={
            "name": "Fresh Organic Spinach",
            "quantity": 2.0,
            "unit": "bags",
            "category": "Produce",
            "expiry_date": "2026-08-30",
        },
    )
    assert add_res.status_code == 201
    item_data = add_res.json()
    assert item_data["name"] == "Fresh Organic Spinach"

    # 2. Fetch Pantry Items
    get_res = client.get("/pantry", headers=headers)
    assert get_res.status_code == 200
    pantry_list = get_res.json()
    assert len(pantry_list) == 1
    assert pantry_list[0]["name"] == "Fresh Organic Spinach"
