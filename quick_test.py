import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_and_view():
    print("=== API Test & Data View ===\n")
    
    # 1. Test connection
    print("1. Testing connection...")
    r = requests.get(f"{BASE_URL}/")
    print(f"   {r.json()}\n")
    
    # 2. Create user
    print("2. Creating user...")
    user = {"full_name": "Test User", "email": "test@example.com"}
    r = requests.post(f"{BASE_URL}/users/", json=user)
    print(f"   {r.json()}")
    
    # 3. View users
    r = requests.get(f"{BASE_URL}/users/")
    users = r.json()["users"]
    print(f"   Users in DB: {len(users)}")
    for u in users: print(f"     - {u['full_name']} ({u['email']})")
    print()
    
    if users:
        user_id = users[0]["id"]
        
        # 4. Create device
        print("3. Creating device...")
        device = {"device_id": "BB001", "user_id": user_id}
        r = requests.post(f"{BASE_URL}/devices/", json=device)
        print(f"   {r.json()}")
        
        # 5. View devices
        r = requests.get(f"{BASE_URL}/devices/")
        devices = r.json()["devices"]
        print(f"   Devices in DB: {len(devices)}")
        for d in devices: print(f"     - {d['device_id']} (User: {d['user_id']})")
        print()
        
        # 6. Create health data
        print("4. Creating health metrics...")
        health = {
            "device_id": "BB001",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "heart_rate": 75,
            "spo2": 98,
            "steps": 1000
        }
        r = requests.post(f"{BASE_URL}/health-metrics/", json=health)
        print(f"   {r.json()}")
        
        # 7. View health data
        r = requests.get(f"{BASE_URL}/health-metrics/")
        metrics = r.json()["health_metrics"]
        print(f"   Health metrics in DB: {len(metrics)}")
        for m in metrics: 
            print(f"     - HR:{m['heart_rate']} SpO2:{m['spo2']} Steps:{m['steps']}")

if __name__ == "__main__":
    try:
        test_and_view()
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")