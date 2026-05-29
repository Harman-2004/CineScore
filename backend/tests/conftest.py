import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Force settings database url to in-memory sqlite and mock TMDb before imports
from app.config import settings
settings.DATABASE_URL = "sqlite:///:memory:"
settings.TMDB_API_KEY = "your_tmdb_api_key_test"

from app.main import app
from app.database import Base, get_db

# Create an in-memory SQLite database for isolated tests
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """
    Creates a fresh, isolated database structure for each test.
    Cleans up completely after completion.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """
    Overrides the FastAPI database dependency with the active test session
    and provides a TestClient instance.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user_token(client):
    """
    Utility fixture to register and log in a test user.
    Returns a dictionary with auth headers.
    """
    user_data = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "testpassword123"
    }
    # Register
    client.post("/api/auth/register", json=user_data)
    
    # Login
    response = client.post("/api/auth/login", json={
        "username_or_email": "testuser",
        "password": "testpassword123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
