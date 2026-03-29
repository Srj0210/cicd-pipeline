import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_home_status(client):
    response = client.get("/")
    assert response.status_code == 200

def test_home_json_structure(client):
    response = client.get("/")
    data = response.get_json()
    assert "service" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "healthy"

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"

def test_info_endpoint(client):
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.get_json()
    assert data["app"] == "cicd-pipeline-demo"
    assert "tech_stack" in data

def test_404_handling(client):
    response = client.get("/nonexistent")
    assert response.status_code == 404
