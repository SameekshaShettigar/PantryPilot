import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    """
    FastAPI TestClient Fixture.
    Allows pytest to simulate HTTP requests against PantryPilot backend endpoints.
    """
    with TestClient(app) as test_client:
        yield test_client
