import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import User, Subject, Lesson, PracticeTask, Quiz


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def session():
    # Create the database
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


def test_create_user(client):
    response = client.post(
        "/users/",
        json={"email": "test@example.com", "password": "Test@1234", "username": "testuser", "first_name": "Test", "last_name": "User"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_login(client):
    # Create user first
    client.post(
        "/users/",
        json={"email": "loginuser@example.com", "password": "Test@1234", "username": "loginuser", "first_name": "Login", "last_name": "User"},
    )
    response = client.post(
        "/login",
        json={"email": "loginuser@example.com", "password": "Test@1234"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_read_users_unauthenticated(client):
    response = client.get("/admin/users/")
    assert response.status_code == 401


def test_read_subjects_unauthenticated(client):
    response = client.get("/admin/subjects/")
    assert response.status_code == 401


def test_read_lessons_unauthenticated(client):
    response = client.get("/admin/subjects/1/lessons/")
    assert response.status_code == 401


def test_read_tasks_unauthenticated(client):
    response = client.get("/admin/lessons/1/practice_tasks/")
    assert response.status_code == 401


def test_read_quizzes_unauthenticated(client):
    response = client.get("/admin/lessons/1/quizzes/")
    assert response.status_code == 401
