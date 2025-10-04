from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import requests
import json
import os

app = FastAPI(title="Bio Band Health Monitoring API", version="3.0.0")

# Environment variables
DATABASE_URL = os.getenv("TURSO_DB_URL")
DATABASE_TOKEN = os.getenv("TURSO_DB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def execute_turso_sql(sql, params=None):
    if not DATABASE_TOKEN:
        raise Exception("Database token not configured")
    
    headers = {
        "Authorization": f"Bearer {DATABASE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {"requests": [{"type": "execute", "stmt": {"sql": sql}}]}
    if params:
        # Convert params to proper Turso format
        turso_params = []
        for param in params:
            if param is None:
                turso_params.append({"type": "null", "value": None})
            elif isinstance(param, str):
                turso_params.append({"type": "text", "value": param})
            elif isinstance(param, int):
                turso_params.append({"type": "integer", "value": str(param)})
            elif isinstance(param, float):
                turso_params.append({"type": "float", "value": param})
            else:
                turso_params.append({"type": "text", "value": str(param)})
        data["requests"][0]["stmt"]["args"] = turso_params
    
    try:
        response = requests.post(f"{DATABASE_URL}/v2/pipeline", headers=headers, json=data, timeout=10)
        if response.status_code != 200:
            raise Exception(f"Database error: {response.status_code} - {response.text}")
        return response.json()
    except Exception as e:
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

class MessageRequest(BaseModel):
    message: str
    session_id: str = "default"

sessions = {}

@app.get("/")
def root():
    return {
        "message": "Bio Band Health Monitoring API",
        "status": "success",
        "version": "3.0.0",
        "endpoints": {
            "GET /users/": "Get all users",
            "GET /users/{user_id}": "Get user by ID",
            "POST /users/": "Create user",
            "GET /devices/": "Get all devices",
            "GET /health-metrics/": "Get all health data",
            "GET /health-metrics/device/{device_id}": "Get health data by device",
            "POST /health-metrics/": "Add health data",
            "POST /chat": "AI Health Assistant",
            "GET /chat/{session_id}": "Get chat history"
        }
    }

@app.get("/users/")
def get_all_users():
    try:
        result = execute_turso_sql("SELECT id, full_name, email, created_at FROM users ORDER BY id")
        
        users_data = []
        if result.get("results") and result["results"][0].get("response", {}).get("result", {}).get("rows"):
            rows = result["results"][0]["response"]["result"]["rows"]
            for row in rows:
                users_data.append({
                    "id": row[0]["value"] if isinstance(row[0], dict) and "value" in row[0] else str(row[0]),
                    "full_name": row[1]["value"] if isinstance(row[1], dict) and "value" in row[1] else str(row[1]),
                    "email": row[2]["value"] if isinstance(row[2], dict) and "value" in row[2] else str(row[2]),
                    "created_at": row[3]["value"] if isinstance(row[3], dict) and "value" in row[3] else str(row[3])
                })
        
        return {"success": True, "users": users_data, "count": len(users_data)}
        
    except Exception as e:
        return {"success": False, "error": str(e), "users": [], "count": 0}

@app.get("/users/{user_id}")
def get_user_by_id(user_id: int):
    try:
        result = execute_turso_sql("SELECT id, full_name, email, created_at FROM users WHERE id = ?", [user_id])
        
        if result.get("results") and result["results"][0].get("response", {}).get("result", {}).get("rows"):
            rows = result["results"][0]["response"]["result"]["rows"]
            if rows:
                row = rows[0]
                user_data = {
                    "id": row[0]["value"] if isinstance(row[0], dict) and "value" in row[0] else str(row[0]),
                    "full_name": row[1]["value"] if isinstance(row[1], dict) and "value" in row[1] else str(row[1]),
                    "email": row[2]["value"] if isinstance(row[2], dict) and "value" in row[2] else str(row[2]),
                    "created_at": row[3]["value"] if isinstance(row[3], dict) and "value" in row[3] else str(row[3])
                }
                return {"success": True, "user": user_data}
        
        return {"success": False, "error": "User not found", "user_id": user_id}
        
    except Exception as e:
        return {"success": False, "error": str(e), "user_id": user_id}

@app.post("/users/")
def create_user(user: UserCreate):
    try:
        result = execute_turso_sql("INSERT INTO users (full_name, email) VALUES (?, ?)", [user.full_name, user.email])
        
        if result and result.get("results") and result["results"][0].get("type") == "ok":
            return {"success": True, "message": "User created successfully"}
        else:
            return {"success": False, "message": "Failed to create user", "debug": result}
            
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@app.get("/devices/")
def get_all_devices():
    try:
        result = execute_turso_sql("SELECT id, device_id, user_id, model, status FROM devices ORDER BY id")
        
        devices_data = []
        if result.get("results") and result["results"][0].get("response", {}).get("result", {}).get("rows"):
            rows = result["results"][0]["response"]["result"]["rows"]
            for row in rows:
                devices_data.append({
                    "id": row[0]["value"] if isinstance(row[0], dict) and "value" in row[0] else str(row[0]),
                    "device_id": row[1]["value"] if isinstance(row[1], dict) and "value" in row[1] else str(row[1]),
                    "user_id": row[2]["value"] if isinstance(row[2], dict) and "value" in row[2] else str(row[2]),
                    "model": row[3]["value"] if isinstance(row[3], dict) and "value" in row[3] else str(row[3]),
                    "status": row[4]["value"] if isinstance(row[4], dict) and "value" in row[4] else str(row[4])
                })
        
        return {"success": True, "devices": devices_data, "count": len(devices_data)}
        
    except Exception as e:
        return {"success": False, "error": str(e), "devices": [], "count": 0}

@app.get("/health-metrics/")
def get_all_health_metrics():
    try:
        result = execute_turso_sql("SELECT id, device_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp FROM health_metrics ORDER BY id DESC LIMIT 50")
        
        health_data = []
        if result.get("results") and result["results"][0].get("response", {}).get("result", {}).get("rows"):
            rows = result["results"][0]["response"]["result"]["rows"]
            for row in rows:
                health_data.append({
                    "id": row[0]["value"] if isinstance(row[0], dict) and "value" in row[0] else str(row[0]),
                    "device_id": row[1]["value"] if isinstance(row[1], dict) and "value" in row[1] else str(row[1]),
                    "heart_rate": row[2]["value"] if isinstance(row[2], dict) and "value" in row[2] else row[2],
                    "spo2": row[3]["value"] if isinstance(row[3], dict) and "value" in row[3] else row[3],
                    "temperature": float(row[4]["value"]) if isinstance(row[4], dict) and "value" in row[4] and row[4]["value"] else row[4],
                    "steps": row[5]["value"] if isinstance(row[5], dict) and "value" in row[5] else row[5],
                    "calories": row[6]["value"] if isinstance(row[6], dict) and "value" in row[6] else row[6],
                    "activity": row[7]["value"] if isinstance(row[7], dict) and "value" in row[7] else row[7],
                    "timestamp": row[8]["value"] if isinstance(row[8], dict) and "value" in row[8] else row[8]
                })
        
        return {"success": True, "health_metrics": health_data, "count": len(health_data)}
        
    except Exception as e:
        return {"success": False, "error": str(e), "health_metrics": [], "count": 0}

@app.get("/health-metrics/device/{device_id}")
def get_health_metrics_by_device(device_id: str):
    try:
        result = execute_turso_sql("SELECT id, device_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp FROM health_metrics WHERE device_id = ? ORDER BY timestamp DESC", [device_id])
        
        health_data = []
        if result.get("results") and result["results"][0].get("response", {}).get("result", {}).get("rows"):
            rows = result["results"][0]["response"]["result"]["rows"]
            for row in rows:
                health_data.append({
                    "id": row[0]["value"] if isinstance(row[0], dict) and "value" in row[0] else str(row[0]),
                    "device_id": row[1]["value"] if isinstance(row[1], dict) and "value" in row[1] else str(row[1]),
                    "heart_rate": row[2]["value"] if isinstance(row[2], dict) and "value" in row[2] else row[2],
                    "spo2": row[3]["value"] if isinstance(row[3], dict) and "value" in row[3] else row[3],
                    "temperature": float(row[4]["value"]) if isinstance(row[4], dict) and "value" in row[4] and row[4]["value"] else row[4],
                    "steps": row[5]["value"] if isinstance(row[5], dict) and "value" in row[5] else row[5],
                    "calories": row[6]["value"] if isinstance(row[6], dict) and "value" in row[6] else row[6],
                    "activity": row[7]["value"] if isinstance(row[7], dict) and "value" in row[7] else row[7],
                    "timestamp": row[8]["value"] if isinstance(row[8], dict) and "value" in row[8] else row[8]
                })
        
        return {"success": True, "device_id": device_id, "health_metrics": health_data, "count": len(health_data)}
        
    except Exception as e:
        return {"success": False, "error": str(e), "device_id": device_id, "health_metrics": [], "count": 0}

@app.post("/health-metrics/")
def add_health_metric(data: HealthMetricCreate):
    try:
        # First, ensure the device exists or create it
        device_check = execute_turso_sql("SELECT id FROM devices WHERE device_id = ?", [data.device_id])
        
        if not (device_check and device_check.get("results") and device_check["results"][0].get("response", {}).get("result", {}).get("rows")):
            # Device doesn't exist, create it
            execute_turso_sql(
                "INSERT OR IGNORE INTO devices (device_id, user_id, model, status) VALUES (?, ?, ?, ?)",
                [data.device_id, 1, "BioBand Pro", "active"]
            )
        
        # Insert health metric without foreign key constraints
        result = execute_turso_sql(
            "INSERT INTO health_metrics (device_id, user_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [data.device_id, 1, data.heart_rate, data.spo2, data.temperature, data.steps, data.calories, data.activity, data.timestamp]
        )
        
        # Check if insert was successful
        if result and result.get("results") and result["results"][0].get("type") == "ok":
            # Get the inserted record to confirm
            get_result = execute_turso_sql(
                "SELECT id, device_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp FROM health_metrics WHERE device_id = ? ORDER BY id DESC LIMIT 1",
                [data.device_id]
            )
            
            if get_result and get_result.get("results") and get_result["results"][0].get("response", {}).get("result", {}).get("rows"):
                row = get_result["results"][0]["response"]["result"]["rows"][0]
                inserted_data = {
                    "id": row[0]["value"] if isinstance(row[0], dict) else str(row[0]),
                    "device_id": row[1]["value"] if isinstance(row[1], dict) else str(row[1]),
                    "heart_rate": row[2]["value"] if isinstance(row[2], dict) else row[2],
                    "spo2": row[3]["value"] if isinstance(row[3], dict) else row[3],
                    "temperature": row[4]["value"] if isinstance(row[4], dict) else row[4],
                    "steps": row[5]["value"] if isinstance(row[5], dict) else row[5],
                    "calories": row[6]["value"] if isinstance(row[6], dict) else row[6],
                    "activity": row[7]["value"] if isinstance(row[7], dict) else row[7],
                    "timestamp": row[8]["value"] if isinstance(row[8], dict) else row[8]
                }
                return {
                    "success": True, 
                    "message": "Health metric recorded successfully",
                    "data": inserted_data
                }
        
        return {"success": False, "message": "Failed to insert health metric", "debug": result}
        
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/chat")
async def chat(request: MessageRequest):
    if not GEMINI_API_KEY:
        return {"success": False, "error": "AI service not configured"}
    
    if request.session_id not in sessions:
        sessions[request.session_id] = []
    
    timestamp = datetime.now().isoformat()
    sessions[request.session_id].append({"role": "user", "message": request.message, "timestamp": timestamp})
    
    try:
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
            headers={"Content-Type": "application/json", "X-goog-api-key": GEMINI_API_KEY},
            json={
                "contents": [{"parts": [{"text": f"You are Bio Band AI Assistant. Only answer health questions in simple English. If not health-related, say 'I only help with health questions.' Question: {request.message}"}]}],
                "generationConfig": {"maxOutputTokens": 150}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            ai_response = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            sessions[request.session_id].append({"role": "assistant", "message": ai_response, "timestamp": datetime.now().isoformat()})
            return {"success": True, "response": ai_response.strip(), "session_id": request.session_id}
        else:
            return {"success": False, "error": f"AI API Error: {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/chat/{session_id}")
async def get_chat_history(session_id: str):
    if session_id in sessions:
        return {"success": True, "session_id": session_id, "history": sessions[session_id], "message_count": len(sessions[session_id])}
    return {"success": True, "session_id": session_id, "history": [], "message_count": 0}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "database": "Connected" if DATABASE_TOKEN else "Not configured"}