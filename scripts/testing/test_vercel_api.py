import requests
import json

# Your Vercel URL
VERCEL_URL = "https://test-jez2k3bfw-praveens-projects-79540d8d.vercel.app"

def test_get_users():
    print("Testing GET /users/")
    response = requests.get(f"{VERCEL_URL}/users/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_create_user():
    print("Testing POST /users/")
    user_data = {
        "full_name": "Test User",
        "email": "test@example.com"
    }
    response = requests.post(f"{VERCEL_URL}/users/", json=user_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_api_status():
    print("Testing GET /")
    response = requests.get(f"{VERCEL_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

if __name__ == "__main__":
    print("Testing Vercel API Connection...")
    print(f"Base URL: {VERCEL_URL}")
    print("=" * 50)
    
    test_api_status()
    test_get_users()
    test_create_user()
    
    print("Test completed!")