import requests
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("TURSO_DB_URL")
DATABASE_TOKEN = os.getenv("TURSO_DB_TOKEN")

def test_turso_connection():
    print("Testing Turso Database Connection...")
    print(f"Database URL: {DATABASE_URL}")
    print(f"Token (first 20 chars): {DATABASE_TOKEN[:20]}..." if DATABASE_TOKEN else "No token found")
    
    headers = {
        "Authorization": f"Bearer {DATABASE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Simple test query
    data = {
        "requests": [
            {
                "type": "execute",
                "stmt": {"sql": "SELECT 1 as test"}
            }
        ]
    }
    
    try:
        response = requests.post(f"{DATABASE_URL}/v2/pipeline", headers=headers, json=data, timeout=10)
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ Turso connection successful!")
            return True
        else:
            print(f"❌ Turso connection failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return False

if __name__ == "__main__":
    test_turso_connection()