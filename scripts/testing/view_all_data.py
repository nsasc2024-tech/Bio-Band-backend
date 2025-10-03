import requests
import json

BASE_URL = "https://bio-band-backend.vercel.app"

def view_all_data():
    print("=== BIO BAND DATABASE VIEWER ===\n")
    
    # Get Users
    print("USERS:")
    response = requests.get(f"{BASE_URL}/users/")
    if response.status_code == 200:
        data = response.json()
        for user in data['users']:
            print(f"  ID: {user['id']}, Name: {user['full_name']}, Email: {user['email']}")
        print(f"  Total Users: {data['count']}\n")
    
    # Get Devices
    print("DEVICES:")
    response = requests.get(f"{BASE_URL}/devices/")
    if response.status_code == 200:
        data = response.json()
        for device in data['devices']:
            print(f"  ID: {device['id']}, Device: {device['device_id']}, User: {device['user_id']}, Model: {device['model']}")
        print(f"  Total Devices: {data['count']}\n")
    
    # Get Health Metrics
    print("HEALTH METRICS:")
    response = requests.get(f"{BASE_URL}/health-metrics/")
    if response.status_code == 200:
        data = response.json()
        for metric in data['health_metrics']:
            print(f"  ID: {metric['id']}, Device: {metric['device_id']}, HR: {metric['heart_rate']}, Activity: {metric['activity']}")
        print(f"  Total Health Records: {data['count']}\n")
    
    # Get Chat Messages (try a sample session)
    print("CHAT MESSAGES (sample):")
    response = requests.get(f"{BASE_URL}/chat/test123")
    if response.status_code == 200:
        data = response.json()
        print(f"  Messages in session 'test123': {data['message_count']}")

if __name__ == "__main__":
    view_all_data()