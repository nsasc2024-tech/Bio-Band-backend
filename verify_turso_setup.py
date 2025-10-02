import os
import requests
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("TURSO_DB_URL")
DATABASE_TOKEN = os.getenv("TURSO_DB_TOKEN")

def execute_turso_sql(sql, params=None):
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
    
    if params:
        data["requests"][0]["stmt"]["args"] = params
    
    try:
        response = requests.post(f"{DATABASE_URL}/v2/pipeline", headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def check_tables():
    print("=== Checking Turso Database Tables ===")
    
    # Check if tables exist
    result = execute_turso_sql("SELECT name FROM sqlite_master WHERE type='table'")
    if result and result.get("results"):
        response_result = result["results"][0].get("response", {})
        if "result" in response_result and "rows" in response_result["result"]:
            tables = [row[0]["value"] for row in response_result["result"]["rows"]]
            print(f"Existing tables: {tables}")
            return tables
    return []

def create_tables():
    print("=== Creating Tables ===")
    
    # Create users table
    users_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    # Create devices table
    devices_sql = """
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        model TEXT DEFAULT 'BioBand Pro',
        status TEXT DEFAULT 'active',
        registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """
    
    # Create health_metrics table
    health_metrics_sql = """
    CREATE TABLE IF NOT EXISTS health_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        heart_rate INTEGER,
        spo2 INTEGER,
        temperature REAL,
        steps INTEGER,
        calories INTEGER,
        activity TEXT,
        timestamp DATETIME NOT NULL,
        FOREIGN KEY (device_id) REFERENCES devices(device_id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """
    
    tables = [
        ("users", users_sql),
        ("devices", devices_sql), 
        ("health_metrics", health_metrics_sql)
    ]
    
    for table_name, sql in tables:
        result = execute_turso_sql(sql)
        if result:
            print(f"✓ {table_name} table created/verified")
        else:
            print(f"✗ Failed to create {table_name} table")

def insert_sample_data():
    print("=== Inserting Sample Data ===")
    
    # Insert sample users
    users = [
        ("John Doe", "john@example.com"),
        ("Jane Smith", "jane@example.com")
    ]
    
    for name, email in users:
        result = execute_turso_sql(
            "INSERT OR IGNORE INTO users (full_name, email) VALUES (?, ?)",
            [name, email]
        )
        if result:
            print(f"✓ User {name} inserted")
    
    # Insert sample devices
    devices = [
        ("BAND001", 1, "BioBand Pro", "active"),
        ("BAND002", 2, "BioBand Pro", "active")
    ]
    
    for device_id, user_id, model, status in devices:
        result = execute_turso_sql(
            "INSERT OR IGNORE INTO devices (device_id, user_id, model, status) VALUES (?, ?, ?, ?)",
            [device_id, user_id, model, status]
        )
        if result:
            print(f"✓ Device {device_id} inserted")
    
    # Insert sample health metrics
    health_data = [
        ("BAND001", 1, 78, 97, 36.5, 1250, 55, "Walking", "2025-01-16T10:30:00Z"),
        ("BAND002", 2, 72, 98, 36.2, 8500, 320, "Running", "2025-01-16T09:15:00Z")
    ]
    
    for device_id, user_id, hr, spo2, temp, steps, cal, activity, timestamp in health_data:
        result = execute_turso_sql(
            "INSERT INTO health_metrics (device_id, user_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [device_id, user_id, hr, spo2, temp, steps, cal, activity, timestamp]
        )
        if result:
            print(f"✓ Health data for {device_id} inserted")

def test_data_retrieval():
    print("=== Testing Data Retrieval ===")
    
    # Test users
    result = execute_turso_sql("SELECT * FROM users")
    if result and result.get("results"):
        response_result = result["results"][0].get("response", {})
        if "result" in response_result and "rows" in response_result["result"]:
            rows = response_result["result"]["rows"]
            print(f"Users found: {len(rows)}")
            for row in rows:
                print(f"  - ID: {row[0]['value']}, Name: {row[1]['value']}, Email: {row[2]['value']}")
    
    # Test health metrics
    result = execute_turso_sql("SELECT * FROM health_metrics")
    if result and result.get("results"):
        response_result = result["results"][0].get("response", {})
        if "result" in response_result and "rows" in response_result["result"]:
            rows = response_result["result"]["rows"]
            print(f"Health metrics found: {len(rows)}")

if __name__ == "__main__":
    print("🔍 Verifying Turso Database Setup for Vercel Deployment")
    print(f"Database URL: {DATABASE_URL}")
    print(f"Token configured: {'Yes' if DATABASE_TOKEN else 'No'}")
    print()
    
    # Check existing tables
    existing_tables = check_tables()
    
    # Create tables if they don't exist
    if not existing_tables or len(existing_tables) < 3:
        create_tables()
    
    # Insert sample data
    insert_sample_data()
    
    # Test data retrieval
    test_data_retrieval()
    
    print("\n✅ Database setup verification complete!")