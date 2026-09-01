import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret"

import pytest
from fastapi.testclient import TestClient

from app.db.session import Base, engine
from app.main import app
from app.services.seed import seed_default_roles


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_default_roles()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def disable_external_banguat_lookup(monkeypatch):
    def unavailable_banguat_rate():
        raise RuntimeError("external Banguat lookup disabled in tests")

    monkeypatch.setattr("app.services.remittances.get_banguat_usd_gtq_rate", unavailable_banguat_rate)
