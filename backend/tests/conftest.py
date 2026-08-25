import os
import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Set test DATABASE_URL to in-memory shared SQLite URI BEFORE importing FastAPI app
os.environ["DATABASE_URL"] = "sqlite:///file:memdb1?mode=memory&cache=shared&uri=true"

import pytest
from fastapi.testclient import TestClient
from app.db.database import Base, engine
from app.main import app


@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    """
    Creates database tables in shared in-memory SQLite before tests run and cleans up afterwards.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client():
    """
    FastAPI TestClient Fixture.
    Provides a clean HTTP client for testing backend endpoints.
    """
    with TestClient(app) as test_client:
        yield test_client
