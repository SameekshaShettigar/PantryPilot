from uuid import uuid4


def test_user_registration_and_login(client):
    """
    Tests user registration (POST /auth/register) and login (POST /auth/login).
    Verifies JWT access token issuance.
    """
    unique_user = f"testuser_{uuid4().hex[:6]}"
    email = f"{unique_user}@example.com"
    password = "TestPassword123!"

    # 1. Register User
    reg_response = client.post(
        "/auth/register",
        json={"username": unique_user, "email": email, "password": password},
    )
    assert reg_response.status_code == 201

    # 2. Login User
    login_response = client.post(
        "/auth/login",
        data={"username": unique_user, "password": password},
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
