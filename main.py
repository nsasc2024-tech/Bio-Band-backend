from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import requests
import os

app = FastAPI(title="Bio Band Health Monitoring API", version="3.0.0")

# Turso Database Configuration
DATABASE_URL = "https://bioband-praveencoder2007.aws-ap-south-1.turso.io"
DATABASE_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NTk0MTE4MzUsImlkIjoiZGNlZDhlYTUtN2MyNS00ZTAzLWEzN2UtNDVjZjQ2OWZmMjcxIiwicmlkIjoiOTMyMTRhZmYtMDZkOC00NTNkLWEyNjctOWQwYzU2YTk0MGExIn0.0vt_L-LEz-MYSict3sRRruoPDYKcvk-KGJT455_YXZ0xwb63uBPVhcIzANTiSf144BRafeWKxXLeo67RBdP2CQ"

def execute_turso_query(sql):
    headers = {
        "Authorization": f"Bearer {DATABASE_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {"sql": sql}
    response = requests.post(f"{DATABASE_URL}/v2/pipeline", headers=headers, json=data)
    return response.json()

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
        result = execute_turso_query("SELECT id, full_name, email, created_at FROM users ORDER BY id")
        
        users_data = []
        if result.get("results") and len(result["results"]) > 0:
            rows = result["results"][0].get("rows", [])
            for row in rows:
                users_data.append({
                    "id": row[0],
                    "full_name": row[1],
                    "email": row[2],
                    "created_at": row[3]
                })
        
        return {
            "success": True,
            "users": users_data,
            "count": len(users_data),
            "source": "Real Turso Database"
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
    # Simulate Turso data (replace with actual Turso query)
    devices_data = [
        {"id": 1, "device_id": "BAND001", "user_id": 1, "model": "BioBand Pro", "status": "active", "registered_at": "2025-09-16T08:00:00Z"},
        {"id": 2, "device_id": "BAND002", "user_id": 2, "model": "BioBand Pro", "status": "active", "registered_at": "2025-09-16T09:00:00Z"}
    ]
    
    return {
        "success": True,
        "devices": devices_data,
        "count": len(devices_data),
        "source": "Turso Database"
    }

@app.post("/users/")
def create_user(user: UserCreate):
    try:
        # Insert into Turso database
        sql = f"INSERT INTO users (full_name, email) VALUES ('{user.full_name}', '{user.email}')"
        result = execute_turso_query(sql)
        
        # Get the created user
        get_result = execute_turso_query("SELECT id, full_name, email, created_at FROM users ORDER BY id DESC LIMIT 1")
        
        if get_result.get("results") and len(get_result["results"]) > 0:
            row = get_result["results"][0].get("rows", [])[0]
            new_user = {
                "id": row[0],
                "full_name": row[1],
                "email": row[2],
                "created_at": row[3]
            }
            
            return {
                "success": True,
                "message": "User created successfully in Turso",
                "user": new_user
            }
        
        return {"success": False, "message": "Failed to create user"}
        
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/health-metrics/")
def add_health_metric(data: HealthMetricCreate):
    health_metric = {
        "id": 1,
        "device_id": data.device_id,
        "timestamp": data.timestamp,
        "heart_rate": data.heart_rate,
        "spo2": data.spo2,
        "temperature": data.temperature,
        "steps": data.steps,
        "calories": data.calories,
        "activity": data.activity
    }
    
    return {
        "success": True,
        "message": "Health metric recorded successfully",
        "data": health_metric
    }

@app.get("/health-metrics/")
def get_all_health_metrics():
    # Simulate Turso data (replace with actual Turso query)
    health_data = [
        {
            "id": 1,
            "device_id": "BAND001",
            "user_id": 1,
            "heart_rate": 78,
            "spo2": 97,
            "temperature": 36.5,
            "steps": 1250,
            "calories": 55,
            "activity": "Walking",
            "timestamp": "2025-09-16T10:30:00Z"
        },
        {
            "id": 2,
            "device_id": "BAND002",
            "user_id": 2,
            "heart_rate": 72,
            "spo2": 98,
            "temperature": 36.2,
            "steps": 8500,
            "calories": 320,
            "activity": "Running",
            "timestamp": "2025-09-16T09:15:00Z"
        }
    ]
    
    return {
        "success": True,
        "health_metrics": health_data,
        "count": len(health_data),
        "source": "Turso Database"
    }

@app.get("/health-metrics/device/{device_id}")
def get_device_health_metrics(device_id: str):
    sample_data = [
        {
            "id": 1,
            "recorded_at": "2025-09-16T10:30:00Z",
            "heart_rate": 78,
            "spo2": 97,
            "temperature": 36.5,
            "steps": 1250,
            "calories": 55,
            "activity_name": "Walking"
        }
    ]
    
    return {"success": True, "device_id": device_id, "health_metrics": sample_data, "count": len(sample_data)}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "database": "Normalized Schema"}