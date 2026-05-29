from fastapi.testclient import TestClient

def test_register_user(client: TestClient):
    payload = {
        "email": "alice@example.com",
        "username": "alice",
        "password": "alicepassword"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["username"] == "alice"
    assert "id" in data
    assert "hashed_password" not in data

def test_register_duplicate_user(client: TestClient):
    payload = {
        "email": "alice@example.com",
        "username": "alice",
        "password": "alicepassword"
    }
    # First registration
    client.post("/api/auth/register", json=payload)
    # Second duplicate registration
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_login_user(client: TestClient):
    # Register
    payload = {
        "email": "bob@example.com",
        "username": "bob",
        "password": "bobpassword"
    }
    client.post("/api/auth/register", json=payload)
    
    # Login via JSON
    response = client.post("/api/auth/login", json={
        "username_or_email": "bob",
        "password": "bobpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client: TestClient):
    response = client.post("/api/auth/login", json={
        "username_or_email": "nonexistent",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "Incorrect" in response.json()["detail"]

def test_get_current_user_profile(client: TestClient, test_user_token: dict):
    response = client.get("/api/auth/me", headers=test_user_token)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
