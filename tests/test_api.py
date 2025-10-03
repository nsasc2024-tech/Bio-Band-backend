"""
API endpoint tests for Bio Band Backend
"""
import pytest
import requests

BASE_URL = "https://bio-band-backend.vercel.app"

def test_api_status():
    """Test API status endpoint"""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "version" in data

def test_get_users():
    """Test get users endpoint"""
    response = requests.get(f"{BASE_URL}/users/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "users" in data
    assert "count" in data

def test_health_check():
    """Test health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"