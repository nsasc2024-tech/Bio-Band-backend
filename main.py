from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Bio Band Health Monitoring API", version="3.0.0")

DATABASE_URL = os.getenv("TURSO_DB_URL", "https://bioband-praveencoder2007.aws-ap-south-1.turso.io")
DATABASE_TOKEN = os.getenv("TURSO_DB_TOKEN")

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthMetricCreate(BaseModel):
    device_id: str
    timestamp: str
    heart_rate: Optional[int] = None
    spo2: Optional[int] = None
    temperature: Optional[float] = None
    steps: Optional[int] = None
    calories: Optional[int] = None
    activity: Optional[str] = "Walking"

class UserCreate(BaseModel):
    full_name: str
    email: str

class DeviceCreate(BaseModel):
    device_id: str
    user_id: int
    model: str = "BioBand Pro"

@app.get("/")
def root():
    return {
        "message": "Bio Band Health Monitoring API",
        "status": "success",
        "version": "3.0.0",
        "database_url": "libsql://bioband-praveencoder2007.aws-ap-south-1.turso.io",
        "endpoints": {
            "GET /users/": "Get all users from Turso",
            "GET /devices/": "Get all devices from Turso",
            "GET /health-metrics/": "Get all health data from Turso",
            "POST /users/": "Create user",
            "POST /devices/": "Register device",
            "POST /health-metrics/": "Add health data"
        }
    }

@app.get("/users/")
def get_all_users():
    try:
        result = execute_turso_sql("SELECT id, full_name, email, created_at FROM users ORDER BY id")
        
        users_data = []
        if result.get("results") and len(result["results"]) > 0:
            response_result = result["results"][0].get("response", {})
            if "result" in response_result and "rows" in response_result["result"]:
                rows = response_result["result"]["rows"]
                for row in rows:
                    users_data.append({
                        "id": extract_value(row[0]),
                        "full_name": extract_value(row[1]),
                        "email": extract_value(row[2]),
                        "created_at": extract_value(row[3])
                    })
        
        return {
            "success": True,
            "users": users_data,
            "count": len(users_data),
            "source": "Real Turso Database via HTTP"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "users": [],
            "count": 0,
            "source": "Turso Database Error"
        }

@app.get("/devices/")
def get_all_devices():
    try:
        result = execute_turso_sql("SELECT id, device_id, user_id, model, status, registered_at FROM devices ORDER BY id")
        
        devices_data = []
        if result.get("results") and len(result["results"]) > 0:
            response_result = result["results"][0].get("response", {})
            if "result" in response_result and "rows" in response_result["result"]:
                rows = response_result["result"]["rows"]
                for row in rows:
                    devices_data.append({
                        "id": extract_value(row[0]),
                        "device_id": extract_value(row[1]),
                        "user_id": extract_value(row[2]),
                        "model": extract_value(row[3]),
                        "status": extract_value(row[4]),
                        "registered_at": extract_value(row[5])
                    })
        
        return {
            "success": True,
            "devices": devices_data,
            "count": len(devices_data),
            "source": "Real Turso Database via HTTP"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "devices": [],
            "count": 0,
            "source": "Turso Database Error"
        }

@app.post("/users/")
def create_user(user: UserCreate):
    try:
        execute_turso_sql(
            "INSERT INTO users (full_name, email) VALUES (?, ?)",
            [user.full_name, user.email]
        )
        
        get_result = execute_turso_sql("SELECT id, full_name, email, created_at FROM users WHERE email = ? ORDER BY id DESC LIMIT 1", [user.email])
        
        if get_result.get("results") and len(get_result["results"]) > 0:
            response_result = get_result["results"][0].get("response", {})
            if "result" in response_result and "rows" in response_result["result"]:
                rows = response_result["result"]["rows"]
                if len(rows) > 0:
                    row = rows[0]
                    new_user = {
                        "id": extract_value(row[0]),
                        "full_name": extract_value(row[1]),
                        "email": extract_value(row[2]),
                        "created_at": extract_value(row[3])
                    }
                    
                    return {
                        "success": True,
                        "message": "User created successfully in Turso",
                        "user": new_user
                    }
        
        return {"success": False, "message": "Failed to create user"}
        
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/devices/")
def register_device(device: DeviceCreate):
    try:
        execute_turso_sql(
            "INSERT INTO devices (device_id, user_id, model) VALUES (?, ?, ?)",
            [device.device_id, device.user_id, device.model]
        )
        
        get_result = execute_turso_sql("SELECT id, device_id, user_id, model, status, registered_at FROM devices WHERE device_id = ? ORDER BY id DESC LIMIT 1", [device.device_id])
        
        if get_result.get("results") and len(get_result["results"]) > 0:
            response_result = get_result["results"][0].get("response", {})
            if "result" in response_result and "rows" in response_result["result"]:
                rows = response_result["result"]["rows"]
                if len(rows) > 0:
                    row = rows[0]
                    new_device = {
                        "id": extract_value(row[0]),
                        "device_id": extract_value(row[1]),
                        "user_id": extract_value(row[2]),
                        "model": extract_value(row[3]),
                        "status": extract_value(row[4]),
                        "registered_at": extract_value(row[5])
                    }
                    
                    return {
                        "success": True,
                        "message": "Device registered successfully in Turso",
                        "device": new_device
                    }
        
        return {"success": False, "message": "Failed to register device"}
        
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/health-metrics/")
def add_health_metric(data: HealthMetricCreate):
    try:
        execute_turso_sql(
            "INSERT INTO health_metrics (device_id, user_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [data.device_id, 1, data.heart_rate, data.spo2, data.temperature, data.steps, data.calories, data.activity, data.timestamp]
        )
        
        get_result = execute_turso_sql("SELECT id, device_id, user_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp FROM health_metrics ORDER BY id DESC LIMIT 1")
        
        if get_result.get("results") and len(get_result["results"]) > 0:
            response_result = get_result["results"][0].get("response", {})
            if "result" in response_result and "rows" in response_result["result"]:
                rows = response_result["result"]["rows"]
                if len(rows) > 0:
                    row = rows[0]
                    health_metric = {
                        "id": extract_value(row[0]),
                        "device_id": extract_value(row[1]),
                        "user_id": extract_value(row[2]),
                        "heart_rate": extract_value(row[3]),
                        "spo2": extract_value(row[4]),
                        "temperature": extract_value(row[5]),
                        "steps": extract_value(row[6]),
                        "calories": extract_value(row[7]),
                        "activity": extract_value(row[8]),
                        "timestamp": extract_value(row[9])
                    }
                    
                    return {
                        "success": True,
                        "message": "Health metric recorded successfully in Turso",
                        "data": health_metric
                    }
        
        return {"success": False, "message": "Failed to create health metric"}
        
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@app.get("/health-metrics/")
def get_all_health_metrics():
    try:
        result = execute_turso_sql("SELECT id, device_id, user_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp FROM health_metrics ORDER BY timestamp DESC")
        
        health_data = []
        if result.get("results") and len(result["results"]) > 0:
            response_result = result["results"][0].get("response", {})
            if "result" in response_result and "rows" in response_result["result"]:
                rows = response_result["result"]["rows"]
                for row in rows:
                    health_data.append({
                        "id": extract_value(row[0]),
                        "device_id": extract_value(row[1]),
                        "user_id": extract_value(row[2]),
                        "heart_rate": extract_value(row[3]),
                        "spo2": extract_value(row[4]),
                        "temperature": extract_value(row[5]),
                        "steps": extract_value(row[6]),
                        "calories": extract_value(row[7]),
                        "activity": extract_value(row[8]),
                        "timestamp": extract_value(row[9])
                    })
        
        return {
            "success": True,
            "health_metrics": health_data,
            "count": len(health_data),
            "source": "Real Turso Database via HTTP"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "health_metrics": [],
            "count": 0,
            "source": "Turso Database Error"
        }

@app.get("/health-metrics/device/{device_id}")
def get_device_health_metrics(device_id: str):
    try:
        result = execute_turso_sql(
            "SELECT id, device_id, user_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp FROM health_metrics WHERE device_id = ? ORDER BY timestamp DESC",
            [device_id]
        )
        
        health_data = []
        if result.get("results") and len(result["results"]) > 0:
            response_result = result["results"][0].get("response", {})
            if "result" in response_result and "rows" in response_result["result"]:
                rows = response_result["result"]["rows"]
                for row in rows:
                    health_data.append({
                        "id": extract_value(row[0]),
                        "device_id": extract_value(row[1]),
                        "user_id": extract_value(row[2]),
                        "heart_rate": extract_value(row[3]),
                        "spo2": extract_value(row[4]),
                        "temperature": extract_value(row[5]),
                        "steps": extract_value(row[6]),
                        "calories": extract_value(row[7]),
                        "activity": extract_value(row[8]),
                        "timestamp": extract_value(row[9])
                    })
        
        return {
            "success": True,
            "device_id": device_id,
            "health_metrics": health_data,
            "count": len(health_data),
            "source": "Real Turso Database via HTTP"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "device_id": device_id,
            "health_metrics": [],
            "count": 0,
            "source": "Turso Database Error"
        }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "database": "Normalized Schema"}