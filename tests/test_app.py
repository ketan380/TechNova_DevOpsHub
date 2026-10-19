"""
Automated Test Suite for DevOpsHub
TechNova Cloud Computing Internship Task 4: Docker Containerization
Testing Flask Web Dashboard, REST APIs, and Validation Handlers using pytest and Flask TestClient.
"""

import json
import pytest
from app import app


@pytest.fixture
def client():
    """Create and configure a Flask test client instance."""
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


# =====================================================================
# Home Page & UI Route Tests
# =====================================================================

def test_home_page_status_and_content(client):
    """Test that the home page loads successfully with HTTP 200 and displays DevOpsHub branding."""
    response = client.get("/")
    assert response.status_code == 200
    html_data = response.get_data(as_text=True)
    assert "DevOpsHub" in html_data
    assert "Developer Tools. Simplified." in html_data
    assert "TechNova" in html_data


# =====================================================================
# Health Check Endpoint Tests
# =====================================================================

def test_api_health_endpoint(client):
    """Test that GET /api/health returns HTTP 200 with healthy status, service name, and valid timestamp."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "DevOpsHub"
    assert "version" in data
    assert "uptime_seconds" in data
    assert "timestamp" in data


# =====================================================================
# System Info Endpoint Tests
# =====================================================================

def test_api_info_endpoint(client):
    """Test that GET /api/info returns runtime information and registered endpoints."""
    response = client.get("/api/info")
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert data["app_name"] == "DevOpsHub"
    assert "python_version" in data
    assert "containerized" in data
    assert "available_endpoints" in data
    assert isinstance(data["available_endpoints"], list)
    assert len(data["available_endpoints"]) >= 4


# =====================================================================
# Text Utility API Tests (/api/text/analyze)
# =====================================================================

def test_text_analyze_valid_string(client):
    """Test text analysis with standard multi-line content."""
    payload = {
        "text": "Hello DevOpsHub.\nThis is a containerized Python Flask application."
    }
    response = client.post(
        "/api/text/analyze",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert data["success"] is True
    metrics = data["metrics"]
    assert metrics["word_count"] == 9
    assert metrics["line_count"] == 2
    assert metrics["character_count"] == 66


def test_text_analyze_empty_string(client):
    """Test text analysis with empty string input."""
    payload = {"text": ""}
    response = client.post(
        "/api/text/analyze",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    metrics = data["metrics"]
    assert metrics["word_count"] == 0
    assert metrics["line_count"] == 0
    assert metrics["character_count"] == 0


def test_text_analyze_missing_field(client):
    """Test text analysis with missing 'text' field returns HTTP 400."""
    payload = {"invalid_field": "sample"}
    response = client.post(
        "/api/text/analyze",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "Missing required field: 'text'" in data["error"]


def test_text_analyze_non_string_type(client):
    """Test text analysis with invalid data type (number instead of string) returns HTTP 400."""
    payload = {"text": 12345}
    response = client.post(
        "/api/text/analyze",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "Field 'text' must be a string" in data["error"]


def test_text_analyze_non_json_content_type(client):
    """Test text analysis with invalid content type returns HTTP 400."""
    response = client.post(
        "/api/text/analyze",
        data="Plain text content",
        content_type="text/plain"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False


# =====================================================================
# JSON Formatter and Validator API Tests (/api/json/validate)
# =====================================================================

def test_json_validate_valid_object(client):
    """Test JSON validation with valid JSON string."""
    payload = {
        "json_string": '{"name": "DevOpsHub", "active": true, "version": "1.0"}',
        "indent": 2
    }
    response = client.post(
        "/api/json/validate",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert data["valid"] is True
    assert data["type"] == "dict"
    assert data["item_count"] == 3
    assert "formatted" in data


def test_json_validate_invalid_syntax(client):
    """Test JSON validation with syntax error (missing quote and comma) returns HTTP 400."""
    payload = {
        "json_string": '{"broken": [1, 2, }'
    }
    response = client.post(
        "/api/json/validate",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["valid"] is False
    assert "error" in data
    assert "line" in data
    assert "column" in data


def test_json_validate_empty_string(client):
    """Test JSON validation with empty string input returns HTTP 400."""
    payload = {"json_string": "   "}
    response = client.post(
        "/api/json/validate",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["valid"] is False


def test_json_validate_raw_payload(client):
    """Test JSON validation with direct raw text payload."""
    raw_json = '{"service": "Docker", "healthy": true}'
    response = client.post(
        "/api/json/validate",
        data=raw_json,
        content_type="text/plain"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["valid"] is True
    assert data["type"] == "dict"


# =====================================================================
# Routing, Error Handling & Security Tests
# =====================================================================

def test_nonexistent_api_route_returns_404_json(client):
    """Test that requesting an unknown API route returns HTTP 404 with JSON error."""
    response = client.get("/api/nonexistent_route")
    assert response.status_code == 404
    assert response.is_json
    data = response.get_json()
    assert data["success"] is False
    assert "does not exist" in data["message"]


def test_method_not_allowed_returns_405_json(client):
    """Test that invoking an unsupported HTTP method on an API route returns HTTP 405 with JSON error."""
    response = client.delete("/api/health")
    assert response.status_code == 405
    assert response.is_json
    data = response.get_json()
    assert data["success"] is False
    assert "Method DELETE is not permitted" in data["message"]


def test_security_headers_present(client):
    """Test that response includes modern security headers."""
    response = client.get("/")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
