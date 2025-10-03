from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = FastAPI(title="Bio Band Medical API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Environment Variables
DATABASE_URL = os.getenv("TURSO_DB_URL", "")
DATABASE_TOKEN = os.getenv("TURSO_DB_TOKEN", "")
API_KEY = os.getenv("GEMINI_API_KEY", "dummy_key")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Convert libsql to https
if DATABASE_URL and DATABASE_URL.startswith("libsql://"):
    DATABASE_URL = DATABASE_URL.replace("libsql://", "https://")

user_sessions = {}

# Simple database function
def execute_sql(sql):
    if not DATABASE_URL or not DATABASE_TOKEN:
        return {"error": "Database not configured"}
    
    try:
        headers = {"Authorization": f"Bearer {DATABASE_TOKEN}", "Content-Type": "application/json"}
        data = {"requests": [{"type": "execute", "stmt": {"sql": sql}}]}
        response = requests.post(f"{DATABASE_URL}/v2/pipeline", headers=headers, json=data, timeout=10)
        return response.json() if response.status_code == 200 else {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def extract_value(item):
    return item.get('value') if isinstance(item, dict) else item

# Models
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
    heart_rate: Optional[int] = None
    spo2: Optional[int] = None
    temperature: Optional[float] = None
    steps: Optional[int] = None
    calories: Optional[int] = None
    activity: Optional[str] = "Walking"

@app.get("/")
async def root():
    return {
        "message": "Bio Band Medical API v2.0 is running",
        "features": ["AI Health Assistant", "User Management", "Device Management", "Health Data"],
        "endpoints": {
            "/chat": "POST - AI Health Assistant",
            "/chat/{session_id}": "GET - Chat History",
            "/users/": "GET/POST - User Management",
            "/devices/": "GET/POST - Device Management", 
            "/health-metrics/": "GET/POST - Health Data"
        },
        "database_status": "Connected" if DATABASE_URL and DATABASE_TOKEN else "Not configured"
    }

# Chat APIs
@app.post("/chat")
async def health_chat(request: MessageRequest):
    user_session_key = f"{request.session_id}"
    
    if user_session_key not in user_sessions:
        user_sessions[user_session_key] = []
    
    user_sessions[user_session_key].append({
        "role": "user", 
        "message": request.message, 
        "timestamp": datetime.now()
    })
    
    health_prompt = f"""You are Bio Band AI Assistant. You help with health questions only. Use simple English.

    IMPORTANT: If NOT about health, say: "I can only help with health-related questions."

    For health questions: Give simple, helpful advice. Use everyday words. Keep short. Tell them to see doctor for serious problems.

    Question: {request.message}"""
    
    try:
        if API_KEY == "dummy_key":
            ai_response = "AI service not available. Please configure GEMINI_API_KEY."
        else:
            response = requests.post(
                API_URL,
                headers={"Content-Type": "application/json", "X-goog-api-key": API_KEY},
                json={
                    "contents": [{"parts": [{"text": health_prompt}]}],
                    "generationConfig": {"maxOutputTokens": 500}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                ai_response = f"AI Error: {response.status_code}"
        
        user_sessions[user_session_key].append({
            "role": "assistant", 
            "message": ai_response, 
            "timestamp": datetime.now()
        })
        
        return {
            "response": ai_response.strip(),
            "session_id": request.session_id,
            "timestamp": datetime.now()
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/chat/{session_id}")
async def get_chat_history(session_id: str):
    user_session_key = f"{session_id}"
    
    if user_session_key in user_sessions:
        return {
            "session_id": session_id,
            "history": user_sessions[user_session_key],
            "message_count": len(user_sessions[user_session_key])
        }
    return {"session_id": session_id, "history": [], "message_count": 0}

# User APIs
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
    except Exception as e:
        return {"success": False, "error": str(e), "users": [], "count": 0}

@app.post("/users/")
def create_user(user: UserCreate):
    try:
        sql = f"INSERT INTO users (full_name, email) VALUES ('{user.full_name.replace(\"'\", \"''\")}', '{user.email}')"
        result = execute_sql(sql)
        
        if "error" in result:
            return {"success": False, "message": result["error"]}
        
        return {"success": True, "message": "User created successfully", "user": {"full_name": user.full_name, "email": user.email}}
    except Exception as e:
        return {"success": False, "message": str(e)}

# Device APIs
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
    except Exception as e:
        return {"success": False, "error": str(e), "devices": [], "count": 0}

@app.post("/devices/")
def create_device(device: DeviceCreate):
    try:
        sql = f"INSERT INTO devices (device_id, user_id, model) VALUES ('{device.device_id}', {device.user_id}, '{device.model}')"
        result = execute_sql(sql)
        
        if "error" in result:
            return {"success": False, "message": result["error"]}
        
        return {"success": True, "message": "Device created successfully", "device": {"device_id": device.device_id, "user_id": device.user_id, "model": device.model}}
    except Exception as e:
        return {"success": False, "message": str(e)}

# Health Metrics APIs
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
    except Exception as e:
        return {"success": False, "error": str(e), "health_metrics": [], "count": 0}

@app.post("/health-metrics/")
def create_health_metric(data: HealthMetricCreate):
    try:
        # Simple insert without device checking
        heart_rate_val = data.heart_rate if data.heart_rate is not None else 'NULL'
        spo2_val = data.spo2 if data.spo2 is not None else 'NULL'
        temp_val = data.temperature if data.temperature is not None else 'NULL'
        steps_val = data.steps if data.steps is not None else 'NULL'
        calories_val = data.calories if data.calories is not None else 'NULL'
        
        sql = f"INSERT INTO health_metrics (device_id, user_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp) VALUES ('{data.device_id}', 1, {heart_rate_val}, {spo2_val}, {temp_val}, {steps_val}, {calories_val}, '{data.activity}', '{data.timestamp}')"
        
        result = execute_sql(sql)
        
        if "error" in result:
            return {"success": False, "message": result["error"]}
        
        return {"success": True, "message": "Health metric created successfully", "data": {"device_id": data.device_id, "timestamp": data.timestamp}}
    except Exception as e:
        return {"success": False, "message": str(e)}