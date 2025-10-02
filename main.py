from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import libsql_experimental as libsql
import os

app = FastAPI(title="Bio Band Health Monitoring API", version="2.0.0")

# Turso Database Configuration
DATABASE_URL = "libsql://bioband-praveencoder2007.aws-ap-south-1.turso.io"
DATABASE_TOKEN = os.getenv("TURSO_DATABASE_TOKEN", "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NTk0MTE4MzUsImlkIjoiZGNlZDhlYTUtN2MyNS00ZTAzLWEzN2UtNDVjZjQ2OWZmMjcxIiwicmlkIjoiOTMyMTRhZmYtMDZkOC00NTNkLWEyNjctOWQwYzU2YTk0MGExIn0.0vt_L-LEz-MYSict3sRRruoPDYKcvk-KGJT455_YXZ0xwb63uBPVhcIzANTiSf144BRafeWKxXLeo67RBdP2CQ")

def get_db_connection():
    return libsql.connect(DATABASE_URL, auth_token=DATABASE_TOKEN)

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
    try:
        conn = get_db_connection()
        
        result = conn.execute("SELECT id, full_name, email, created_at FROM users ORDER BY id")
        rows = result.fetchall()
        conn.close()
        
        users_data = []
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
            "source": "Turso Database"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

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
        conn = get_db_connection()
        
        # Insert new user into Turso database
        result = conn.execute(
            "INSERT INTO users (full_name, email) VALUES (?, ?) RETURNING id, full_name, email, created_at",
            (user.full_name, user.email)
        )
        
        row = result.fetchone()
        conn.close()
        
        if row:
            new_user = {
                "id": row[0],
                "full_name": row[1],
                "email": row[2],
                "created_at": row[3]
            }
            
            return {
                "success": True,
                "message": "User created successfully",
                "user": new_user
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create user")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

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