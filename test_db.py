import requests
import os

DATABASE_URL = "https://bioband-nsasc2024-tech.aws-ap-south-1.turso.io"
DATABASE_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NTk0NzU2NzUsImlkIjoiYzdkOTBjNDctYzMyMS00MWExLWI4ZjktMTE3MDA1NTQxMjkzIiwicmlkIjoiMjE3MWJlNjYtNWE4ZS00M2EzLWI0MTMtYWU1NjlmYmZmNzg1In0.5pMXpEGOXlLPd0IDsRMwFOSb6mTqEhgQr7TGd8BqhSLBNFEwaIEe-M26ufXFsiNLHf5hqixALCK6qeRXa-t1CQ"

def test_db():
    headers = {"Authorization": f"Bearer {DATABASE_TOKEN}", "Content-Type": "application/json"}
    data = {"requests": [{"type": "execute", "stmt": {"sql": "SELECT COUNT(*) FROM users"}}]}
    
    try:
        response = requests.post(f"{DATABASE_URL}/v2/pipeline", headers=headers, json=data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    result = test_db()
    if result:
        print("Database connection successful!")
        print(result)
    else:
        print("Database connection failed!")