from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import HealthMetricCreate, UserCreate, DeviceCreate
from datetime import datetime

app = FastAPI(title="Bio Band Health Monitoring API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Bio Band Health Monitoring API",
        "status": "success",
        "version": "2.0.0",
        "database_url": "libsql://bio-hand-praveen123.aws-ap-south-1.turso.io",
        "endpoints": {
            "Health Metrics": {
                "POST /health-metrics/": "Add health data",
                "GET /health-metrics/": "Get all health data",
                "GET /health-metrics/device/{device_id}": "Get device data"
            },
            "Users": {
                "POST /users/": "Create user",
                "GET /users/": "Get all users"
            },
            "Devices": {
                "POST /devices/": "Register device",
                "GET /devices/": "Get all devices"
            }
        }
    }

def get_activity_type_id(activity_name: str) -> int:
    activity_map = {
        "Walking": 1, "Running": 2, "Cycling": 3, 
        "Resting": 4, "Swimming": 5
    }
    return activity_map.get(activity_name, 1)

def get_user_from_device(device_id: str) -> int:
    device_user_map = {
        "WATCH001": 1, "BB001": 2
    }
    return device_user_map.get(device_id, 1)

@app.post("/health-metrics/")
def add_health_metric(data: HealthMetricCreate):
    user_id = get_user_from_device(data.device_id)
    activity_type_id = get_activity_type_id(data.activity or "Walking")
    recorded_at = data.timestamp or datetime.now().isoformat()
    
    health_metric = {
        "id": 1,
        "device_id": data.device_id,
        "user_id": user_id,
        "recorded_at": recorded_at,
        "heart_rate": data.heart_rate,
        "spo2": data.spo2,
        "temperature": data.temperature,
        "steps": data.steps,
        "calories": data.calories,
        "activity_type_id": activity_type_id,
        "activity_name": data.activity
    }
    
    return {
        "success": True,
        "message": "Health metric recorded successfully",
        "data": health_metric
    }

@app.get("/health-metrics/")
def get_all_health_metrics():
    sample_data = [
        {
            "id": 1,
            "device_id": "WATCH001",
            "user_id": 1,
            "recorded_at": "2025-09-16T10:30:00Z",
            "heart_rate": 78,
            "spo2": 97,
            "temperature": 36.5,
            "steps": 1250,
            "calories": 55,
            "activity_name": "Walking"
        }
    ]
    
    return {
        "success": True,
        "health_metrics": sample_data,
        "count": len(sample_data)
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
    
    return {
        "success": True,
        "device_id": device_id,
        "health_metrics": sample_data,
        "count": len(sample_data)
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "Normalized Schema"
    }