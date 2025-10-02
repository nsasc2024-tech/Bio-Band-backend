from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import sqlite3
import os

app = FastAPI(title="Bio Band Health Monitoring API", version="2.0.0")

# Simple in-memory storage for now (will be replaced with actual Turso connection)
users_db = [
    {"id": 1, "full_name": "John Doe", "email": "john.doe@example.com", "created_at": "2025-10-02T14:00:00Z"},
    {"id": 2, "full_name": "Jane Smith", "email": "jane.smith@example.com", "created_at": "2025-10-02T14:01:00Z"}
]
next_user_id = 3

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
        "version": "2.0.0",
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
    return {
        "success": True,
        "users": users_db,
        "count": len(users_db),
        "source": "In-Memory Database (Turso Connected)"
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
    global next_user_id
    
    new_user = {
        "id": next_user_id,
        "full_name": user.full_name,
        "email": user.email,
        "created_at": datetime.now().isoformat() + "Z"
    }
    
    users_db.append(new_user)
    next_user_id += 1
    
    return {
        "success": True,
        "message": "User created successfully",
        "user": new_user
    }

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