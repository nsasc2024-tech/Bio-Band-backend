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

# Turso Database Configuration
DATABASE_URL = os.getenv("TURSO_DB_URL")
DATABASE_TOKEN = os.getenv("TURSO_DB_TOKEN")
if DATABASE_URL and DATABASE_URL.startswith("libsql://"):
    DATABASE_URL = DATABASE_URL.replace("libsql://", "https://")

# Gemini AI Configuration
API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

if not API_KEY:
    print("Warning: GEMINI_API_KEY not found.")
    API_KEY = "dummy_key"

user_sessions = {}

# Database Functions
def execute_turso_sql(sql):
    headers = {
        "Authorization": f"Bearer {DATABASE_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {"requests": [{"type": "execute", "stmt": {"sql": sql}}]}
    
    try:
        response = requests.post(f"{DATABASE_URL}/v2/pipeline", headers=headers, json=data, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Database connection failed: {str(e)}")

def extract_value(item):
    return item.get('value') if isinstance(item, dict) else item

# Pydantic Models
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
        "features": ["AI Health Assistant with Gemini", "User Management", "Device Management", "Health Data Tracking"],
        "endpoints": {
            "/chat": "POST - Chat with Gemini AI",
            "/chat/{session_id}": "GET - Chat History",
            "/users/": "GET/POST - User Management",
            "/devices/": "GET/POST - Device Management",
            "/health-metrics/": "GET/POST - Health Data"
        }
    }

# AI Chat APIs
@app.post("/chat")
async def health_chat(request: MessageRequest):
    """AI Health Assistant - Chat with Gemini AI"""
    user_session_key = f"{request.session_id}"
    
    if user_session_key not in user_sessions:
        user_sessions[user_session_key] = []
    
    user_sessions[user_session_key].append({
        "role": "user", 
        "message": request.message, 
        "timestamp": datetime.now()
    })
    
    health_prompt = f"""You are Bio Band AI Assistant, a health advisor for Bio Band users. You help with health questions only. Use simple English words.

    IMPORTANT: If the question is NOT about health (like math, games, movies, etc.), say EXACTLY: "I can only help with health-related questions."

    For health questions:
    - Give simple, helpful advice
    - Use everyday words
    - Keep answers short and clear
    - Tell them to see a doctor for serious problems

    Question: {request.message}

    Remember: Only health questions. Use simple words. Keep it short."""
    
    try:
        response = requests.post(
            API_URL,
            headers={
                "Content-Type": "application/json",
                "X-goog-api-key": API_KEY,
            },
            json={
                "contents": [{
                    "parts": [{"text": health_prompt}]
                }],
                "generationConfig": {"maxOutputTokens": 500}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data["candidates"][0]["content"]["parts"][0]["text"]
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
        else:
            return {"error": f"API Error {response.status_code}: {response.text}"}
            
    except Exception as e:
        return {"error": str(e)}

@app.get("/chat/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    user_session_key = f"{session_id}"
    
    if user_session_key in user_sessions:
        return {
            "session_id": session_id,
            "history": user_sessions[user_session_key],
            "message_count": len(user_sessions[user_session_key])
        }
    return {"session_id": session_id, "history": [], "message_count": 0}

# User Management APIs
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
            "source": "Turso Database"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "users": [], "count": 0}

@app.post("/users/")
def create_user(user: UserCreate):
    try:
        sql = f"INSERT INTO users (full_name, email) VALUES ('{user.full_name.replace(\"'\", \"''\")}', '{user.email}')"
        insert_result = execute_turso_sql(sql)
        
        if insert_result.get("results") and len(insert_result["results"]) > 0:
            result_info = insert_result["results"][0]
            if result_info.get("type") == "ok":
                get_result = execute_turso_sql(f"SELECT id, full_name, email, created_at FROM users WHERE email = '{user.email}' ORDER BY id DESC LIMIT 1")
                
                if get_result.get("results") and len(get_result["results"]) > 0:
                    response_result = get_result["results"][0].get("response", {})
                    if "result" in response_result and "rows" in response_result["result"]:
                        rows = response_result["result"]["rows"]
                        if len(rows) > 0:
                            row = rows[0]
                            return {
                                "success": True,
                                "message": "User created successfully",
                                "user": {
                                    "id": extract_value(row[0]),
                                    "full_name": extract_value(row[1]),
                                    "email": extract_value(row[2]),
                                    "created_at": extract_value(row[3])
                                }
                            }
            else:
                error_msg = result_info.get("error", {}).get("message", "Unknown error")
                if "UNIQUE constraint failed" in error_msg:
                    return {"success": False, "message": "Email already exists"}
                return {"success": False, "message": f"Database error: {error_msg}"}
        
        return {"success": False, "message": "Failed to create user"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

# Device Management APIs
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
            "source": "Turso Database"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "devices": [], "count": 0}

@app.post("/devices/")
def register_device(device: DeviceCreate):
    try:
        sql = f"INSERT INTO devices (device_id, user_id, model) VALUES ('{device.device_id}', {device.user_id}, '{device.model}')"
        insert_result = execute_turso_sql(sql)
        
        if insert_result.get("results") and len(insert_result["results"]) > 0:
            result_info = insert_result["results"][0]
            if result_info.get("type") == "ok":
                get_result = execute_turso_sql(f"SELECT id, device_id, user_id, model, status, registered_at FROM devices WHERE device_id = '{device.device_id}' ORDER BY id DESC LIMIT 1")
                
                if get_result.get("results") and len(get_result["results"]) > 0:
                    response_result = get_result["results"][0].get("response", {})
                    if "result" in response_result and "rows" in response_result["result"]:
                        rows = response_result["result"]["rows"]
                        if len(rows) > 0:
                            row = rows[0]
                            return {
                                "success": True,
                                "message": "Device registered successfully",
                                "device": {
                                    "id": extract_value(row[0]),
                                    "device_id": extract_value(row[1]),
                                    "user_id": extract_value(row[2]),
                                    "model": extract_value(row[3]),
                                    "status": extract_value(row[4]),
                                    "registered_at": extract_value(row[5])
                                }
                            }
        
        return {"success": False, "message": "Failed to register device"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

# Health Metrics APIs
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
            "source": "Turso Database"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "health_metrics": [], "count": 0}

@app.post("/health-metrics/")
def add_health_metric(data: HealthMetricCreate):
    try:
        # Auto-create device if it doesn't exist
        device_check = execute_turso_sql(f"SELECT user_id FROM devices WHERE device_id = '{data.device_id}' LIMIT 1")
        
        user_id = 1
        if device_check.get("results") and len(device_check["results"]) > 0:
            response_result = device_check["results"][0].get("response", {})
            if "result" in response_result and "rows" in response_result["result"]:
                rows = response_result["result"]["rows"]
                if len(rows) > 0:
                    user_id = extract_value(rows[0][0])
                else:
                    create_device_sql = f"INSERT INTO devices (device_id, user_id, model) VALUES ('{data.device_id}', 1, 'BioBand Pro')"
                    execute_turso_sql(create_device_sql)
        
        # Insert health metric
        heart_rate_val = data.heart_rate if data.heart_rate is not None else 'NULL'
        spo2_val = data.spo2 if data.spo2 is not None else 'NULL'
        temp_val = data.temperature if data.temperature is not None else 'NULL'
        steps_val = data.steps if data.steps is not None else 'NULL'
        calories_val = data.calories if data.calories is not None else 'NULL'
        
        sql = f"INSERT INTO health_metrics (device_id, user_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp) VALUES ('{data.device_id}', {user_id}, {heart_rate_val}, {spo2_val}, {temp_val}, {steps_val}, {calories_val}, '{data.activity}', '{data.timestamp}')"
        
        insert_result = execute_turso_sql(sql)
        
        if insert_result.get("results") and len(insert_result["results"]) > 0:
            result_info = insert_result["results"][0]
            if result_info.get("type") == "ok":
                return {
                    "success": True,
                    "message": "Health metric recorded successfully",
                    "data": {
                        "device_id": data.device_id,
                        "user_id": str(user_id),
                        "heart_rate": str(data.heart_rate) if data.heart_rate else None,
                        "spo2": str(data.spo2) if data.spo2 else None,
                        "temperature": data.temperature,
                        "steps": str(data.steps) if data.steps else None,
                        "calories": str(data.calories) if data.calories else None,
                        "activity": data.activity,
                        "timestamp": data.timestamp
                    }
                }
            else:
                error_msg = result_info.get("error", {}).get("message", "Unknown error")
                return {"success": False, "message": f"Database error: {error_msg}"}
        
        return {"success": False, "message": "Failed to create health metric"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}