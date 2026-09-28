"""
Tests for Polymer API endpoints (/api/polymers).
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_list_polymers():
    """Verify listing polymers returns reference polymers."""
    response = client.get("/api/polymers")
    assert response.status_code == 200
    polymers = response.json()
    assert len(polymers) >= 5
    soluplus = next((p for p in polymers if p["polymer_id"] == "POL-005-2026"), None)
    assert soluplus is not None
    assert soluplus["polymer_name"] == "Soluplus"
    assert soluplus["is_reference"] is True


def test_get_polymer_by_id():
    """Verify retrieving specific polymer profile."""
    response = client.get("/api/polymers/POL-005-2026")
    assert response.status_code == 200
    p = response.json()
    assert p["polymer_id"] == "POL-005-2026"
    assert abs(p["tg_k"] - 343.15) < 0.2



def test_get_nonexistent_polymer():
    """Verify 404 for unknown polymer."""
    response = client.get("/api/polymers/POL-NONEXISTENT")
    assert response.status_code == 404


def test_list_polymers_core_only():
    """Verify that core_only=true returns exactly the 8 verified core polymers POL-0001..POL-0008."""
    response = client.get("/api/polymers?core_only=true")
    assert response.status_code == 200
    polymers = response.json()
    assert len(polymers) == 8
    ids = [p["polymer_id"] for p in polymers]
    expected_ids = [f"POL-{i:04d}" for i in range(1, 9)]
    assert sorted(ids) == sorted(expected_ids)


def test_get_polymer_by_normalized_id():
    """Verify POL-1 resolves to POL-0001."""
    response = client.get("/api/polymers/POL-1")
    assert response.status_code == 200
    p = response.json()
    assert p["polymer_id"] == "POL-0001"
    assert p["polymer_name"] == "Eudragit L 100"
