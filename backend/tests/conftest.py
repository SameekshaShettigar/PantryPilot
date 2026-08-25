import os
import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from fastapi.testclient import TestClient

# Set test database to a local SQLite file for consistent cross-thread testing
os.environ["DATABASE_URL"] = "sqlite:///./test_ci.db"

from app.db.database import Base, engine
from app.main import app


@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    """
    Creates test database tables before tests run and cleans up afterwards.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    # Remove temporary test database file
    db_file = Path("./test_ci.db")
    if db_file.exists():
        try:
            db_file.unlink()
        except Exception:
            pass


@pytest.fixture(scope="module")
def client():
    """
    FastAPI TestClient Fixture.
    Provides a clean HTTP client for testing backend endpoints.
    """
    with TestClient(app) as test_client:
        yield test_client
