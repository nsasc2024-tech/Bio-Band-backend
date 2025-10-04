from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import requests
import json
import os

app = FastAPI(title="Bio Band Health Monitoring API", version="3.0.0")

# Turso Database Configuration
DATABASE_URL = os.getenv("TURSO_DB_URL", "https://bioband-nsasc2024-tech.aws-ap-south-1.turso.io")
DATABASE_TOKEN = os.getenv("TURSO_DB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def execute_turso_sql(sql, params=None):
    headers = {
        "Authorization": f"Bearer {DATABASE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "requests": [
            {
                "type": "execute",
                "stmt": {
                    "sql": sql
                }
            }
        ]
    }
    
    if params:
        data["requests"][0]["stmt"]["args"] = params
    
    try:
        response = requests.post(f"{DATABASE_URL}/v2/pipeline", headers=headers, json=data, timeout=10)
        response.raise_for_status()
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
        "database_url": "libsql://bioband-nsasc2024-tech.aws-ap-south-1.turso.io",
        "endpoints": {
            "GET /users/": "Get all users from Turso",
            "POST /users/": "Create user",
            "GET /devices/": "Get all devices from Turso",
            "GET /health-metrics/": "Get all health data from Turso",
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
        if result.get("results") and len(result["results"]) > 0:
            response_result = result["results"][0].get("response", {})
            if "result" in response_result and "rows" in response_result["result"]:
                rows = response_result["result"]["rows"]
                for row in rows:
                    users_data.append({
                        "id": row[0]["value"] if isinstance(row[0], dict) else row[0],
                        "full_name": row[1]["value"] if isinstance(row[1], dict) else row[1],
                        "email": row[2]["value"] if isinstance(row[2], dict) else row[2],
                        "created_at": row[3]["value"] if isinstance(row[3], dict) else row[3]
                    })
        
        return {
            "success": True,
            "users": users_data,
            "count": len(users_data)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "users": [],
            "count": 0
        }

@app.post("/users/")
def create_user(user: UserCreate):
    try:
        insert_result = execute_turso_sql(
            "INSERT INTO users (full_name, email) VALUES (?, ?)",
            [user.full_name, user.email]
        )
        
        if insert_result.get("results"):
            get_result = execute_turso_sql("SELECT id, full_name, email, created_at FROM users ORDER BY id DESC LIMIT 1")
            
            if get_result.get("results") and len(get_result["results"]) > 0:
                response_result = get_result["results"][0].get("response", {})
                if "result" in response_result and "rows" in response_result["result"]:
                    rows = response_result["result"]["rows"]
                    if len(rows) > 0:
                        row = rows[0]
                        new_user = {
                            "id": row[0]["value"] if isinstance(row[0], dict) else row[0],
                            "full_name": row[1]["value"] if isinstance(row[1], dict) else row[1],
                            "email": row[2]["value"] if isinstance(row[2], dict) else row[2],
                            "created_at": row[3]["value"] if isinstance(row[3], dict) else row[3]
                        }
                        
                        return {
                            "success": True,
                            "message": "User created successfully",
                            "user": new_user
                        }
        
        return {"success": False, "message": "Failed to create user"}
        
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

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
                        "id": row[0]["value"] if isinstance(row[0], dict) else row[0],
                        "device_id": row[1]["value"] if isinstance(row[1], dict) else row[1],
                        "user_id": row[2]["value"] if isinstance(row[2], dict) else row[2],
                        "model": row[3]["value"] if isinstance(row[3], dict) else row[3],
                        "status": row[4]["value"] if isinstance(row[4], dict) else row[4],
                        "registered_at": row[5]["value"] if isinstance(row[5], dict) else row[5]
                    })
        
        return {
            "success": True,
            "devices": devices_data,
            "count": len(devices_data)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "devices": [],
            "count": 0
        }

@app.get("/health-metrics/")
def get_all_health_metrics():
    try:
        result = execute_turso_sql("SELECT id, device_id, user_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp FROM health_metrics ORDER BY id DESC")
        
        health_data = []
        if result.get("results") and len(result["results"]) > 0:
            response_result = result["results"][0].get("response", {})
            if "result" in response_result and "rows" in response_result["result"]:
                rows = response_result["result"]["rows"]
                for row in rows:
                    health_data.append({
                        "id": row[0]["value"] if isinstance(row[0], dict) else row[0],
                        "device_id": row[1]["value"] if isinstance(row[1], dict) else row[1],
                        "user_id": row[2]["value"] if isinstance(row[2], dict) else row[2],
                        "heart_rate": row[3]["value"] if isinstance(row[3], dict) else row[3],
                        "spo2": row[4]["value"] if isinstance(row[4], dict) else row[4],
                        "temperature": row[5]["value"] if isinstance(row[5], dict) else row[5],
                        "steps": row[6]["value"] if isinstance(row[6], dict) else row[6],
                        "calories": row[7]["value"] if isinstance(row[7], dict) else row[7],
                        "activity": row[8]["value"] if isinstance(row[8], dict) else row[8],
                        "timestamp": row[9]["value"] if isinstance(row[9], dict) else row[9]
                    })
        
        return {
            "success": True,
            "health_metrics": health_data,
            "count": len(health_data)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "health_metrics": [],
            "count": 0
        }

@app.post("/health-metrics/")
def add_health_metric(data: HealthMetricCreate):
    try:
        user_id = 1  # Default user for now
        
        insert_result = execute_turso_sql(
            "INSERT INTO health_metrics (device_id, user_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [data.device_id, user_id, data.heart_rate, data.spo2, data.temperature, data.steps, data.calories, data.activity, data.timestamp]
        )
        
        if insert_result.get("results"):
            return {
                "success": True,
                "message": "Health metric recorded successfully",
                "data": {
                    "device_id": data.device_id,
                    "timestamp": data.timestamp,
                    "heart_rate": data.heart_rate,
                    "spo2": data.spo2,
                    "temperature": data.temperature,
                    "steps": data.steps,
                    "calories": data.calories,
                    "activity": data.activity
                }
            }
        
        return {"success": False, "message": "Failed to record health metric"}
        
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/chat")
async def chat(request: MessageRequest):
    if not GEMINI_API_KEY:
        return {"success": False, "error": "AI service not configured"}
    
    if request.session_id not in sessions:
        sessions[request.session_id] = []
    
    timestamp = datetime.now().isoformat()
    sessions[request.session_id].append({
        "role": "user", 
        "message": request.message,
        "timestamp": timestamp
    })
    
    try:
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
            headers={
                "Content-Type": "application/json",
                "X-goog-api-key": GEMINI_API_KEY,
            },
            json={
                "contents": [{
                    "parts": [{"text": f"You are Bio Band AI Assistant, a health companion for Bio Band users. You act as a mini doctor providing health-related assistance. Use simple English words that everyone can understand. If the question is not health-related, respond with 'I cannot help with that, I only assist with health-related queries.' Current question: {request.message}"}]
                }],
                "generationConfig": {"maxOutputTokens": 150}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data["candidates"][0]["content"]["parts"][0]["text"]
            sessions[request.session_id].append({
                "role": "assistant", 
                "message": ai_response,
                "timestamp": datetime.now().isoformat()
            })
            return {
                "success": True,
                "response": ai_response.strip().replace("**", "").replace("*", ""),
                "session_id": request.session_id,
                "timestamp": timestamp
            }
        else:
            return {"success": False, "error": f"API Error: {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/chat/{session_id}")
async def get_chat_history(session_id: str):
    if session_id in sessions:
        return {
            "success": True,
            "session_id": session_id, 
            "history": sessions[session_id],
            "message_count": len(sessions[session_id])
        }
    return {
        "success": True,
        "session_id": session_id, 
        "history": [],
        "message_count": 0
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "database": "Turso Connected"}