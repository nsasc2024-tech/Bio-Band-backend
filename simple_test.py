import os
import requests
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("TURSO_DB_URL")
DATABASE_TOKEN = os.getenv("TURSO_DB_TOKEN")

def execute_turso_sql(sql):
    headers = {
        "Authorization": f"Bearer {DATABASE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "requests": [
            {
                "type": "execute",
                "stmt": {
                    "sql": sql
                }
            }
        ]
    }
    
    try:
        response = requests.post(f"{DATABASE_URL}/v2/pipeline", headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# Test basic connection
print("Testing Turso connection...")
result = execute_turso_sql("SELECT 1 as test")
if result:
    print("Connection successful!")
    print("Response:", result)
else:
    print("Connection failed!")