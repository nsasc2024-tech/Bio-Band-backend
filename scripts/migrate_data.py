#!/usr/bin/env python3
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def execute_sql(sql):
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

# Insert sample users from API response
users_data = [
    ("John Doe", "john.doe@example.com", "2025-10-02 13:50:29"),
    ("Jane Smith", "jane.smith@example.com", "2025-10-02 13:50:31"),
    ("John Doe", "john@example.com", "2025-10-02 15:02:41"),
    ("Jane Smith", "jane@example.com", "2025-10-02 15:02:41"),
    ("Praveen Test", "praveen.test@example.com", "2025-10-02 15:18:29"),
    ("jeevith payaluga", "javithwithgirls@gmail.com", "2025-10-02 15:46:33"),
    ("jeevith", "javithwith@gmail.com", "2025-10-02 15:50:55"),
    ("sanjeevan", "sanjeev.test@example.com", "2025-10-03 07:03:53")
]

print("Migrating users data...")
for full_name, email, created_at in users_data:
    sql = f"INSERT INTO users (full_name, email, created_at) VALUES ('{full_name}', '{email}', '{created_at}');"
    result = execute_sql(sql)
    print(f"Added: {full_name} - {result}")

print("\nData migration complete!")