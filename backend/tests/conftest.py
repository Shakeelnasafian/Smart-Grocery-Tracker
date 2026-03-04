"""Shared test fixtures for the Smart Grocery Tracker API."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import User
from app.routers.auth import get_password_hash

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    """
    Provide a DB session bound to an outer transaction that is rolled back after each
    test, ensuring proper isolation even when the code under test calls session.commit().
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    # Patch the app dependency so the test client uses the same connection
    app.dependency_overrides[get_db] = lambda: session
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture()
def client(db):
    return TestClient(app)


@pytest.fixture()
def test_user(db):
    user = User(email="test@example.com", hashed_password=get_password_hash("testpassword123"))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def auth_headers(client, test_user):
    response = client.post(
        "/token",
        data={"username": "test@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
