from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import os
import requests
import json

app = FastAPI()

# Simple in-memory storage for testing
users_db = []
devices_db = []
health_data_db = []
user_counter = 1
device_counter = 1
data_counter = 1

@app.get("/")
def root():
    return {
        "message": "Bio Band Health Monitoring API",
        "status": "success",
        "endpoints": {
            "POST /users/": "Create user",
            "GET /users/all": "Get all users",
            "POST /devices/": "Register device",
            "GET /devices/all": "Get all devices",
            "POST /health-data/": "Add health data",
            "GET /health-data/all": "Get all health data",
            "GET /health-data/user/{user_id}": "Get user's health data"
        }
    }

class UserCreate(BaseModel):
    full_name: str
    email: str
    age: Optional[int] = None

class DeviceCreate(BaseModel):
    device_id: str
    user_id: int
    model: str

class HealthDataCreate(BaseModel):
    user_id: int
    device_id: str
    heart_rate: Optional[int] = None
    spo2: Optional[int] = None
    temperature: Optional[float] = None
    steps: Optional[int] = None
    calories: Optional[int] = None
    activity: Optional[str] = None

@app.post("/users/")
def create_user(user: UserCreate):
    global user_counter
    
    new_user = {
        "id": user_counter,
        "full_name": user.full_name,
        "email": user.email,
        "age": user.age,
        "created_at": "2024-09-28T16:00:00Z"
    }
    users_db.append(new_user)
    
    # Try to save to Turso
    try:
        turso_url = "https://bio-hand-praveen123.aws-ap-south-1.turso.io/v1/execute"
        headers = {
            "Authorization": f"Bearer {os.getenv('TURSO_DB_TOKEN', 'eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicm8iLCJpYXQiOjE3NTkwODAyMTMsImlkIjoiNDcyMWI0MzItODgyYi00MTVkLWI3YzQtNWQyZjk5ZTFkODVlIiwicmlkIjoiYjM4YTdkNjctNzcwMi00OTIxLWIwOTEtZTI0ODI2MzIyNmJmIn0.i8h9_arPOgflWPMGsC5jwTOa97g3ICpr7Q1z5c-6TLCzXLU__j5UEgcSj5dc-vd_1fpv2I7Pxq4FnXDGCYSPDQ')}",
            "Content-Type": "application/json"
        }
        
        data = {
            "statements": [{
                "stmt": f"INSERT INTO users (full_name, email) VALUES ('{user.full_name}', '{user.email}')"
            }]
        }
        
        response = requests.post(turso_url, headers=headers, json=data)
        turso_success = response.status_code == 200
    except:
        turso_success = False
    
    user_counter += 1
    
    return {
        "success": True,
        "id": new_user["id"],
        "full_name": user.full_name,
        "email": user.email,
        "saved_to_turso": turso_success
    }

@app.get("/users/all")
def get_all_users():
    return {
        "success": True,
        "users": users_db,
        "count": len(users_db)
    }

@app.post("/devices/")
def register_device(device: DeviceCreate):
    global device_counter
    
    new_device = {
        "id": device_counter,
        "device_id": device.device_id,
        "user_id": device.user_id,
        "model": device.model,
        "registered_at": "2024-09-28T16:00:00Z"
    }
    devices_db.append(new_device)
    
    device_counter += 1
    
    return {
        "success": True,
        "id": new_device["id"],
        "device_id": device.device_id,
        "user_id": device.user_id,
        "model": device.model
    }

@app.get("/devices/all")
def get_all_devices():
    return {
        "success": True,
        "devices": devices_db,
        "count": len(devices_db)
    }

@app.post("/health-data/")
def add_health_data(data: HealthDataCreate):
    global data_counter
    
    new_data = {
        "id": data_counter,
        "user_id": data.user_id,
        "device_id": data.device_id,
        "heart_rate": data.heart_rate,
        "spo2": data.spo2,
        "temperature": data.temperature,
        "steps": data.steps,
        "calories": data.calories,
        "activity": data.activity,
        "timestamp": "2024-09-28T16:00:00Z"
    }
    health_data_db.append(new_data)
    
    data_counter += 1
    
    return {
        "success": True,
        "id": new_data["id"],
        "user_id": data.user_id,
        "health_metrics": {
            "heart_rate": data.heart_rate,
            "spo2": data.spo2,
            "temperature": data.temperature,
            "steps": data.steps,
            "calories": data.calories,
            "activity": data.activity
        }
    }

@app.get("/health-data/all")
def get_all_health_data():
    return {
        "success": True,
        "health_data": health_data_db,
        "count": len(health_data_db)
    }

@app.get("/health-data/user/{user_id}")
def get_user_health_data(user_id: int):
    user_data = [data for data in health_data_db if data["user_id"] == user_id]
    return {
        "success": True,
        "user_id": user_id,
        "health_data": user_data,
        "count": len(user_data)
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)