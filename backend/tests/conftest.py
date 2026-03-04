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


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def test_user(db):
    user = User(email="test@example.com", hashed_password=get_password_hash("testpassword123"))
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.delete(user)
    db.commit()


@pytest.fixture()
def auth_headers(client, test_user):
    response = client.post(
        "/token",
        data={"username": "test@example.com", "password": "testpassword123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
