import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.api.deps import AuthenticatedUser, get_current_user
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
    Base.metadata.create_all(bind=engine)

    current_user = {"id": "user-owner", "email": "owner@example.com"}

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    def override_get_current_user():
        return AuthenticatedUser(**current_user)

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        test_client.current_user = current_user
        test_client.session_factory = TestingSessionLocal
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def create_org(client: TestClient):
    def _create_org(name: str = "Acme Support") -> dict:
        response = client.post("/v1/organizations", json={"name": name})
        assert response.status_code == 201
        return response.json()

    return _create_org
