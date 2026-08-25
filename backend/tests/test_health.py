def test_health_check(client):
    """
    Tests the GET /health endpoint to verify API server health.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
