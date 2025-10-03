import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("TURSO_DB_URL")
DATABASE_TOKEN = os.getenv("TURSO_DB_TOKEN")

def query_turso(sql):
    headers = {
        "Authorization": f"Bearer {DATABASE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "requests": [
            {
                "type": "execute",
                "stmt": {"sql": sql}
            }
        ]
    }
    
    response = requests.post(f"{DATABASE_URL}/v2/pipeline", headers=headers, json=data)
    return response.json()

def extract_value(item):
    return item.get('value') if isinstance(item, dict) else item

print("=== HEALTH METRICS QUERIES ===")

# Check health metrics count
print("\n1. HEALTH METRICS COUNT:")
result = query_turso("SELECT COUNT(*) as count FROM health_metrics")
if result.get("results") and len(result["results"]) > 0:
    response_result = result["results"][0].get("response", {})
    if "result" in response_result and "rows" in response_result["result"]:
        rows = response_result["result"]["rows"]
        if rows:
            count = extract_value(rows[0][0])
            print(f"Total health records: {count}")

# Check all health metrics
print("\n2. ALL HEALTH METRICS:")
result = query_turso("SELECT * FROM health_metrics ORDER BY id DESC")
if result.get("results") and len(result["results"]) > 0:
    response_result = result["results"][0].get("response", {})
    if "result" in response_result and "rows" in response_result["result"]:
        rows = response_result["result"]["rows"]
        if rows:
            for row in rows:
                print(f"ID: {extract_value(row[0])}, Device: {extract_value(row[1])}, HR: {extract_value(row[3])}, SpO2: {extract_value(row[4])}, Activity: {extract_value(row[8])}, Time: {extract_value(row[9])}")
        else:
            print("No health metrics found")

print("\n=== MANUAL QUERIES FOR TURSO CLI ===")
print("SELECT * FROM health_metrics;")
print("SELECT COUNT(*) FROM health_metrics;")
print("SELECT * FROM health_metrics WHERE device_id = 'BAND001';")
print("SELECT h.*, u.full_name FROM health_metrics h JOIN users u ON h.user_id = u.id;")