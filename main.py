from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# Turso Database
DATABASE_URL = os.getenv("TURSO_DB_URL", "")
DATABASE_TOKEN = os.getenv("TURSO_DB_TOKEN", "")

if DATABASE_URL and DATABASE_URL.startswith("libsql://"):
    DATABASE_URL = DATABASE_URL.replace("libsql://", "https://")

def execute_sql(sql):
    if not DATABASE_URL or not DATABASE_TOKEN:
        return {"error": "Database not configured"}
    
    try:
        headers = {"Authorization": f"Bearer {DATABASE_TOKEN}", "Content-Type": "application/json"}
        data = {"requests": [{"type": "execute", "stmt": {"sql": sql}}]}
        response = requests.post(f"{DATABASE_URL}/v2/pipeline", headers=headers, json=data, timeout=10)
        return response.json() if response.status_code == 200 else {"error": "Database error"}
    except:
        return {"error": "Connection failed"}

def extract_value(item):
    return item.get('value') if isinstance(item, dict) else item

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageRequest(BaseModel):
    message: str
    session_id: str = "default"

class UserCreate(BaseModel):
    full_name: str
    email: str

class DeviceCreate(BaseModel):
    device_id: str
    user_id: int
    model: str = "BioBand Pro"

class HealthMetricCreate(BaseModel):
    device_id: str
    timestamp: str
    heart_rate: int = None
    spo2: int = None
    temperature: float = None
    steps: int = None
    calories: int = None
    activity: str = "Walking"

@app.get("/")
def root():
    return {
        "message": "Bio Band Medical API v2.0 is running",
        "status": "success"
    }

@app.post("/chat")
def chat(request: MessageRequest):
    return {
        "response": "Hello! I'm Bio Band AI Assistant.",
        "session_id": request.session_id
    }

@app.get("/users/")
def get_users():
    try:
        result = execute_sql("SELECT id, full_name, email, created_at FROM users ORDER BY id")
        
        if "error" in result:
            return {"success": False, "error": result["error"], "users": [], "count": 0}
        
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
        
        return {"success": True, "users": users_data, "count": len(users_data)}
    except:
        return {"success": True, "users": [], "count": 0}

@app.post("/users/")
def create_user(user: UserCreate):
    try:
        sql = f"INSERT INTO users (full_name, email) VALUES ('{user.full_name.replace("'", "''")}', '{user.email}')"
        result = execute_sql(sql)
        
        if "error" in result:
            return {"success": False, "message": result["error"]}
        
        return {"success": True, "message": "User created successfully"}
    except:
        return {"success": False, "message": "Failed to create user"}

@app.get("/devices/")
def get_devices():
    try:
        result = execute_sql("SELECT id, device_id, user_id, model, status, registered_at FROM devices ORDER BY id")
        
        if "error" in result:
            return {"success": False, "error": result["error"], "devices": [], "count": 0}
        
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
        
        return {"success": True, "devices": devices_data, "count": len(devices_data)}
    except:
        return {"success": True, "devices": [], "count": 0}

@app.post("/devices/")
def create_device(device: DeviceCreate):
    try:
        sql = f"INSERT INTO devices (device_id, user_id, model) VALUES ('{device.device_id}', {device.user_id}, '{device.model}')"
        result = execute_sql(sql)
        
        if "error" in result:
            return {"success": False, "message": result["error"]}
        
        return {"success": True, "message": "Device created successfully"}
    except:
        return {"success": False, "message": "Failed to create device"}

@app.get("/health-metrics/")
def get_health_metrics():
    try:
        result = execute_sql("SELECT id, device_id, user_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp FROM health_metrics ORDER BY timestamp DESC")
        
        if "error" in result:
            return {"success": False, "error": result["error"], "health_metrics": [], "count": 0}
        
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
        
        return {"success": True, "health_metrics": health_data, "count": len(health_data)}
    except:
        return {"success": True, "health_metrics": [], "count": 0}

@app.post("/health-metrics/")
def create_health_metric(data: HealthMetricCreate):
    try:
        heart_rate_val = data.heart_rate if data.heart_rate is not None else 'NULL'
        spo2_val = data.spo2 if data.spo2 is not None else 'NULL'
        temp_val = data.temperature if data.temperature is not None else 'NULL'
        steps_val = data.steps if data.steps is not None else 'NULL'
        calories_val = data.calories if data.calories is not None else 'NULL'
        
        sql = f"INSERT INTO health_metrics (device_id, user_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp) VALUES ('{data.device_id}', 1, {heart_rate_val}, {spo2_val}, {temp_val}, {steps_val}, {calories_val}, '{data.activity}', '{data.timestamp}')"
        
        result = execute_sql(sql)
        
        if "error" in result:
            return {"success": False, "message": result["error"]}
        
        return {"success": True, "message": "Health metric created successfully"}
    except:
        return {"success": False, "message": "Failed to create health metric"}