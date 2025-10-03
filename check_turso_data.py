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

print("=== CHECKING TURSO DATABASE ===")

# Check users
print("\n1. USERS TABLE:")
result = query_turso("SELECT * FROM users ORDER BY id")
if result.get("results") and len(result["results"]) > 0:
    response_result = result["results"][0].get("response", {})
    if "result" in response_result and "rows" in response_result["result"]:
        rows = response_result["result"]["rows"]
        for row in rows:
            print(f"ID: {extract_value(row[0])}, Name: {extract_value(row[1])}, Email: {extract_value(row[2])}, Created: {extract_value(row[3])}")

# Check devices
print("\n2. DEVICES TABLE:")
result = query_turso("SELECT * FROM devices ORDER BY id")
if result.get("results") and len(result["results"]) > 0:
    response_result = result["results"][0].get("response", {})
    if "result" in response_result and "rows" in response_result["result"]:
        rows = response_result["result"]["rows"]
        for row in rows:
            print(f"ID: {extract_value(row[0])}, Device: {extract_value(row[1])}, User: {extract_value(row[2])}, Model: {extract_value(row[3])}")

# Check health metrics
print("\n3. HEALTH METRICS TABLE:")
result = query_turso("SELECT * FROM health_metrics ORDER BY id")
if result.get("results") and len(result["results"]) > 0:
    response_result = result["results"][0].get("response", {})
    if "result" in response_result and "rows" in response_result["result"]:
        rows = response_result["result"]["rows"]
        for row in rows:
            print(f"ID: {extract_value(row[0])}, Device: {extract_value(row[1])}, HR: {extract_value(row[3])}, SpO2: {extract_value(row[4])}, Activity: {extract_value(row[8])}")

print("\n=== TURSO QUERIES TO RUN MANUALLY ===")
print("1. SELECT * FROM users;")
print("2. SELECT * FROM devices;") 
print("3. SELECT * FROM health_metrics;")
print("4. SELECT COUNT(*) FROM users;")
print("5. SELECT COUNT(*) FROM devices;")
print("6. SELECT COUNT(*) FROM health_metrics;")