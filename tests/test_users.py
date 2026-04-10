import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.database import Base, get_db
from app.security import get_password_hash, verify_password

# Use a separate test database to avoid dropping dev data
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/test_db"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    # Setup: Create tables before each test
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown: Drop tables after each test to ensure a clean state
    Base.metadata.drop_all(bind=engine)

# --- Unit Tests ---
def test_password_hashing():
    password = "supersecretpassword"
    hashed = get_password_hash(password)
    assert password != hashed  # Ensure it is actually hashed
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

# --- Integration Tests ---
def test_create_user_success():
    payload = {
        "username": "testuser", 
        "email": "test@example.com", 
        "password": "password123"
    }
    response = client.post("/users/", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password_hash" not in data  # Validate secure output
    assert "password" not in data

def test_create_user_duplicate_email():
    payload1 = {"username": "user1", "email": "test@example.com", "password": "pw"}
    payload2 = {"username": "user2", "email": "test@example.com", "password": "pw"}
    
    client.post("/users/", json=payload1)
    response = client.post("/users/", json=payload2)
    
    assert response.status_code == 400
    assert "already registered" in response.json()["error"]

def test_invalid_email_schema():
    payload = {"username": "user1", "email": "not-an-email", "password": "pw"}
    response = client.post("/users/", json=payload)
    assert response.status_code == 400