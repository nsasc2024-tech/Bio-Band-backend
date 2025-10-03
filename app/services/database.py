import requests
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("TURSO_DB_URL")
DATABASE_TOKEN = os.getenv("TURSO_DB_TOKEN")

# Ensure URL is HTTPS for HTTP API
if DATABASE_URL and DATABASE_URL.startswith("libsql://"):
    DATABASE_URL = DATABASE_URL.replace("libsql://", "https://")

def execute_turso_sql(sql, params=None):
    headers = {
        "Authorization": f"Bearer {DATABASE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    stmt = {"sql": sql}
    if params:
        stmt["args"] = [{"type": "text", "value": str(p)} if isinstance(p, str) else {"type": "integer", "value": str(p)} if isinstance(p, int) else {"type": "float", "value": str(p)} for p in params]
    
    data = {"requests": [{"type": "execute", "stmt": stmt}]}
    
    try:
        response = requests.post(f"{DATABASE_URL}/v2/pipeline", headers=headers, json=data, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Database connection failed: {str(e)}")

def extract_value(item):
    return item.get('value') if isinstance(item, dict) else item