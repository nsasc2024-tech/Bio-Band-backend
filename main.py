from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Bio Band Health Monitoring API", version="3.0.0")

# Turso Database Configuration
DATABASE_URL = os.getenv("TURSO_DB_URL", "https://bioband-praveencoder2007.aws-ap-south-1.turso.io")
DATABASE_TOKEN = os.getenv("TURSO_DB_TOKEN")

def execute_turso_sql(sql, params=None):
    headers = {
        "Authorization": f"Bearer {DATABASE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Correct Turso HTTP API format
    stmt = {"sql": sql}
    if params:
        stmt["args"] = params
    
    data = {
        "requests": [
            {
                "type": "execute",
                "stmt": stmt
            }
        ]
    }
    
    try:
        response = requests.post(f"{DATABASE_URL}/v2/pipeline", headers=headers, json=data, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Database connection failed: {str(e)}")

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

def get_activity_type_id(activity_name: str) -> int:
    activity_map = {"Walking": 1, "Running": 2, "Cycling": 3, "Resting": 4, "Swimming": 5}
    return activity_map.get(activity_name, 1)

def get_user_from_device(device_id: str) -> int:
    device_user_map = {"WATCH001": 1, "BB001": 2}
    return device_user_map.get(device_id, 1)

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
                        "id": row[0].get('value') if isinstance(row[0], dict) else row[0],
                        "full_name": row[1].get('value') if isinstance(row[1], dict) else row[1],
                        "email": row[2].get('value') if isinstance(row[2], dict) else row[2],
                        "created_at": row[3].get('value') if isinstance(row[3], dict) else row[3]
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
                        "id": row[0],
                        "device_id": row[1],
                        "user_id": row[2],
                        "model": row[3],
                        "status": row[4],
                        "registered_at": row[5]
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
        # Insert into Turso database
        execute_turso_sql(
            "INSERT INTO users (full_name, email) VALUES (?, ?)",
            [user.full_name, user.email]
        )
        
        # Get the newly created user
        get_result = execute_turso_sql("SELECT id, full_name, email, created_at FROM users WHERE email = ? ORDER BY id DESC LIMIT 1", [user.email])
        
        if get_result.get("results") and len(get_result["results"]) > 0:
            response_result = get_result["results"][0].get("response", {})
            if "result" in response_result and "rows" in response_result["result"]:
                rows = response_result["result"]["rows"]
                if len(rows) > 0:
                    row = rows[0]
                    new_user = {
                        "id": row[0].get('value') if isinstance(row[0], dict) else row[0],
                        "full_name": row[1].get('value') if isinstance(row[1], dict) else row[1],
                        "email": row[2].get('value') if isinstance(row[2], dict) else row[2],
                        "created_at": row[3].get('value') if isinstance(row[3], dict) else row[3]
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
        # Insert device into Turso database
        insert_result = execute_turso_sql(
            "INSERT INTO devices (device_id, user_id, model) VALUES (?, ?, ?)",
            [device.device_id, device.user_id, device.model]
        )
        
        if insert_result.get("results") and len(insert_result["results"]) > 0:
            # Get the newly created device
            get_result = execute_turso_sql("SELECT id, device_id, user_id, model, status, registered_at FROM devices ORDER BY id DESC LIMIT 1")
            
            if get_result.get("results") and len(get_result["results"]) > 0:
                response_result = get_result["results"][0].get("response", {})
                if "result" in response_result and "rows" in response_result["result"]:
                    rows = response_result["result"]["rows"]
                    if len(rows) > 0:
                        row = rows[0]
                        new_device = {
                            "id": row[0],
                            "device_id": row[1],
                            "user_id": row[2],
                            "model": row[3],
                            "status": row[4],
                            "registered_at": row[5]
                        }
                        
                        return {
                            "success": True,
                            "message": "Device registered successfully in Turso",
                            "device": new_device
                        }
        
        return {"success": False, "message": "Failed to register device", "debug": insert_result}
        
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/health-metrics/")
def add_health_metric(data: HealthMetricCreate):
    try:
        # Get user_id from device_id (you might want to query devices table for this)
        user_id = get_user_from_device(data.device_id)
        
        # Insert into Turso database
        insert_result = execute_turso_sql(
            "INSERT INTO health_metrics (device_id, user_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [data.device_id, user_id, data.heart_rate, data.spo2, data.temperature, data.steps, data.calories, data.activity, data.timestamp]
        )
        
        if insert_result.get("results") and len(insert_result["results"]) > 0:
            # Get the newly created health metric
            get_result = execute_turso_sql("SELECT id, device_id, user_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp FROM health_metrics ORDER BY id DESC LIMIT 1")
            
            if get_result.get("results") and len(get_result["results"]) > 0:
                response_result = get_result["results"][0].get("response", {})
                if "result" in response_result and "rows" in response_result["result"]:
                    rows = response_result["result"]["rows"]
                    if len(rows) > 0:
                        row = rows[0]
                        health_metric = {
                            "id": row[0],
                            "device_id": row[1],
                            "user_id": row[2],
                            "heart_rate": row[3],
                            "spo2": row[4],
                            "temperature": row[5],
                            "steps": row[6],
                            "calories": row[7],
                            "activity": row[8],
                            "timestamp": row[9]
                        }
                        
                        return {
                            "success": True,
                            "message": "Health metric recorded successfully in Turso",
                            "data": health_metric
                        }
        
        return {"success": False, "message": "Failed to create health metric", "debug": insert_result}
        
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
                        "id": row[0],
                        "device_id": row[1],
                        "user_id": row[2],
                        "heart_rate": row[3],
                        "spo2": row[4],
                        "temperature": row[5],
                        "steps": row[6],
                        "calories": row[7],
                        "activity": row[8],
                        "timestamp": row[9]
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
                        "id": row[0],
                        "device_id": row[1],
                        "user_id": row[2],
                        "heart_rate": row[3],
                        "spo2": row[4],
                        "temperature": row[5],
                        "steps": row[6],
                        "calories": row[7],
                        "activity": row[8],
                        "timestamp": row[9]
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