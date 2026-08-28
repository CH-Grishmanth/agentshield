import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add workspace directory to path so we can import from backend
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.main import app
from backend.database import verify_connection

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data

def test_dashboard_endpoint():
    db_connected, _ = verify_connection()
    response = client.get("/api/dashboard")
    if db_connected:
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert "tools" in data
        assert "apis" in data
        assert "datasources" in data
        assert "policies" in data
        assert "risk_distribution" in data
    else:
        assert response.status_code == 500

def test_agents_list():
    db_connected, _ = verify_connection()
    response = client.get("/api/agents")
    if db_connected:
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            agent = data[0]
            assert "id" in agent
            assert "name" in agent
            assert "risk_level" in agent
    else:
        assert response.status_code == 500

def test_agent_details():
    db_connected, _ = verify_connection()
    # Test with agent-support from seed data
    response = client.get("/api/agents/agent-support")
    if db_connected:
        assert response.status_code == 200
        data = response.json()
        assert "agent" in data
        assert "tools" in data
        assert "risk_score" in data
        assert "score" in data["risk_score"]
    else:
        assert response.status_code in [404, 500]

def test_agent_not_found():
    db_connected, _ = verify_connection()
    response = client.get("/api/agents/non-existent-agent-id")
    if db_connected:
        assert response.status_code == 404
    else:
        assert response.status_code in [404, 500]

def test_risk_paths():
    db_connected, _ = verify_connection()
    response = client.get("/api/agents/agent-support/risk-paths")
    if db_connected:
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    else:
        assert response.status_code in [404, 500]

def test_blast_radius():
    db_connected, _ = verify_connection()
    response = client.get("/api/tools/tool-db-reader/blast-radius")
    if db_connected:
        assert response.status_code == 200
        data = response.json()
        assert "tool" in data
        assert "affected_agents" in data
        assert "affected_datasources" in data
    else:
        assert response.status_code in [404, 500]

def test_policy_violations():
    db_connected, _ = verify_connection()
    response = client.get("/api/policies/violations")
    if db_connected:
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    else:
        assert response.status_code == 500
