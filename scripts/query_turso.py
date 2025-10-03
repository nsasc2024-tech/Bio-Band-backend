#!/usr/bin/env python3
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def query_turso(sql):
    url = "https://bioband-nsasc2024-tech.aws-ap-south-1.turso.io/v2/pipeline"
    token = os.getenv('TURSO_DB_TOKEN')
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "requests": [
            {
                "type": "execute",
                "stmt": {
                    "sql": sql
                }
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Show all tables
print("=== TABLES IN DATABASE ===")
result = query_turso("SELECT name FROM sqlite_master WHERE type='table';")
print(json.dumps(result, indent=2))

# Show table schemas
tables = ['users', 'devices', 'health_metrics', 'chat_messages']
for table in tables:
    print(f"\n=== {table.upper()} TABLE SCHEMA ===")
    result = query_turso(f"PRAGMA table_info({table});")
    print(json.dumps(result, indent=2))
    
    print(f"\n=== {table.upper()} DATA ===")
    result = query_turso(f"SELECT * FROM {table} LIMIT 10;")
    print(json.dumps(result, indent=2))