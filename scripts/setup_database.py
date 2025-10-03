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

# Create tables
print("Creating users table...")
users_sql = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""
result = execute_sql(users_sql)
print(json.dumps(result, indent=2))

print("\nCreating devices table...")
devices_sql = """
CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    model TEXT DEFAULT 'BioBand Pro',
    status TEXT DEFAULT 'active',
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
"""
result = execute_sql(devices_sql)
print(json.dumps(result, indent=2))

print("\nCreating health_metrics table...")
health_sql = """
CREATE TABLE IF NOT EXISTS health_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    heart_rate INTEGER,
    spo2 INTEGER,
    temperature REAL,
    steps INTEGER,
    calories INTEGER,
    activity TEXT DEFAULT 'Walking',
    timestamp DATETIME NOT NULL,
    FOREIGN KEY (device_id) REFERENCES devices (device_id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);
"""
result = execute_sql(health_sql)
print(json.dumps(result, indent=2))

print("\nCreating chat_messages table...")
chat_sql = """
CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""
result = execute_sql(chat_sql)
print(json.dumps(result, indent=2))

print("\nDatabase setup complete!")