import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("TURSO_DB_URL")
DATABASE_TOKEN = os.getenv("TURSO_DB_TOKEN")

def test_turso_connection():
    headers = {
        "Authorization": f"Bearer {DATABASE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Test creating tables
    create_tables = [
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            model TEXT DEFAULT 'BioBand Pro',
            status TEXT DEFAULT 'active',
            registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS health_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            heart_rate INTEGER,
            spo2 INTEGER,
            temperature REAL,
            steps INTEGER,
            calories INTEGER,
            activity TEXT,
            timestamp DATETIME NOT NULL
        )"""
    ]
    
    for sql in create_tables:
        data = {
            "requests": [{"type": "execute", "stmt": {"sql": sql}}]
        }
        
        try:
            response = requests.post(f"{DATABASE_URL}/v2/pipeline", headers=headers, json=data)
            print(f"Table creation: {response.status_code}")
        except Exception as e:
            print(f"Error creating tables: {e}")
    
    # Test inserting sample data
    sample_data = [
        "INSERT OR IGNORE INTO users (full_name, email) VALUES ('John Doe', 'john@example.com')",
        "INSERT OR IGNORE INTO users (full_name, email) VALUES ('Jane Smith', 'jane@example.com')",
        "INSERT OR IGNORE INTO devices (device_id, user_id, model) VALUES ('BAND001', 1, 'BioBand Pro')",
        "INSERT OR IGNORE INTO devices (device_id, user_id, model) VALUES ('BAND002', 2, 'BioBand Pro')"
    ]
    
    for sql in sample_data:
        data = {
            "requests": [{"type": "execute", "stmt": {"sql": sql}}]
        }
        
        try:
            response = requests.post(f"{DATABASE_URL}/v2/pipeline", headers=headers, json=data)
            print(f"Sample data insert: {response.status_code}")
        except Exception as e:
            print(f"Error inserting data: {e}")
    
    print("Turso database setup complete!")

if __name__ == "__main__":
    test_turso_connection()