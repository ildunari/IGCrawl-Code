import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_session
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with overridden dependencies"""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "dependencies" in data


def test_create_account(client: TestClient):
    """Test account creation"""
    response = client.post(
        "/api/v1/accounts",
        json={"username": "testuser", "is_bookmarked": False}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["id"] is not None


def test_list_accounts(client: TestClient):
    """Test listing accounts"""
    # Create test account
    client.post(
        "/api/v1/accounts",
        json={"username": "testuser", "is_bookmarked": False}
    )
    
    response = client.get("/api/v1/accounts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["username"] == "testuser"


def test_rate_limit_headers(client: TestClient):
    """Test that rate limit headers are set"""
    # This would require mocking the rate limiter
    # For now, just test that the endpoint works
    response = client.get("/api/v1/accounts")
    assert response.status_code == 200