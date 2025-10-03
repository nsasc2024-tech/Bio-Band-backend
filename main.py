from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Bio Band Health Monitoring API", version="3.0.0")

DATABASE_URL = os.getenv("TURSO_DB_URL")
if DATABASE_URL and DATABASE_URL.startswith("libsql://"):
    DATABASE_URL = DATABASE_URL.replace("libsql://", "https://")
DATABASE_TOKEN = os.getenv("TURSO_DB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# User chat sessions
user_sessions = {}

def execute_turso_sql(sql, params=None):
    headers = {
        "Authorization": f"Bearer {DATABASE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    stmt = {"sql": sql}
    if params:
        stmt["args"] = [{"type": "text", "value": str(p)} if isinstance(p, str) else {"type": "integer", "value": str(p)} if isinstance(p, int) else {"type": "float", "value": str(p)} for p in params]
    
    data = {"requests": [{"type": "execute", "stmt": stmt}]}
    
    try:
        response = requests.post(f"{DATABASE_URL}/v2/pipeline", headers=headers, json=data, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Database connection failed: {str(e)}")

def extract_value(item):
    return item.get('value') if isinstance(item, dict) else item

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

class DeviceCreate(BaseModel):
    device_id: str
    user_id: int
    model: str = "BioBand Pro"

class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"

@app.get("/")
def root():
    return {
        "message": "Bio Band Health Monitoring API",
        "status": "success",
        "version": "4.0.0 - AI Enabled",
        "database_url": DATABASE_URL,
        "endpoints": {
            "GET /users/": "Get all users from Turso",
            "GET /devices/": "Get all devices from Turso",
            "GET /health-metrics/": "Get all health data from Turso",
            "POST /users/": "Create user",
            "POST /devices/": "Register device",
            "POST /health-metrics/": "Add health data",
            "POST /chat/": "AI Health Assistant",
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
                        "id": extract_value(row[0]),
                        "full_name": extract_value(row[1]),
                        "email": extract_value(row[2]),
                        "created_at": extract_value(row[3])
                    })
        
        return {
            "success": True,
            "users": users_data,
            "count": len(users_data),
            "source": "Real Turso Database via HTTP"
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
            "source": "Real Turso Database via HTTP"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "devices": [],
            "count": 0,
            "source": "Turso Database Error"
        }

@app.post("/users/")
def create_user(user: UserCreate):
    try:
        # Use direct SQL without parameters
        sql = f"INSERT INTO users (full_name, email) VALUES ('{user.full_name.replace("'", "''")}', '{user.email}')"
        insert_result = execute_turso_sql(sql)
        
        # Check if insert was successful
        if insert_result.get("results") and len(insert_result["results"]) > 0:
            result_info = insert_result["results"][0]
            if result_info.get("type") == "ok":
                # Get the newly created user
                get_result = execute_turso_sql(f"SELECT id, full_name, email, created_at FROM users WHERE email = '{user.email}' ORDER BY id DESC LIMIT 1")
                
                if get_result.get("results") and len(get_result["results"]) > 0:
                    response_result = get_result["results"][0].get("response", {})
                    if "result" in response_result and "rows" in response_result["result"]:
                        rows = response_result["result"]["rows"]
                        if len(rows) > 0:
                            row = rows[0]
                            new_user = {
                                "id": extract_value(row[0]),
                                "full_name": extract_value(row[1]),
                                "email": extract_value(row[2]),
                                "created_at": extract_value(row[3])
                            }
                            
                            return {
                                "success": True,
                                "message": "User created successfully in Turso",
                                "user": new_user
                            }
            else:
                error_msg = result_info.get("error", {}).get("message", "Unknown error")
                if "UNIQUE constraint failed" in error_msg:
                    return {"success": False, "message": "Email already exists"}
                else:
                    return {"success": False, "message": f"Database error: {error_msg}"}
        
        return {"success": False, "message": "Failed to create user"}
        
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/devices/")
def register_device(device: DeviceCreate):
    try:
        sql = f"INSERT INTO devices (device_id, user_id, model) VALUES ('{device.device_id}', {device.user_id}, '{device.model}')"
        execute_turso_sql(sql)
        
        get_result = execute_turso_sql("SELECT id, device_id, user_id, model, status, registered_at FROM devices WHERE device_id = ? ORDER BY id DESC LIMIT 1", [device.device_id])
        
        if get_result.get("results") and len(get_result["results"]) > 0:
            response_result = get_result["results"][0].get("response", {})
            if "result" in response_result and "rows" in response_result["result"]:
                rows = response_result["result"]["rows"]
                if len(rows) > 0:
                    row = rows[0]
                    new_device = {
                        "id": extract_value(row[0]),
                        "device_id": extract_value(row[1]),
                        "user_id": extract_value(row[2]),
                        "model": extract_value(row[3]),
                        "status": extract_value(row[4]),
                        "registered_at": extract_value(row[5])
                    }
                    
                    return {
                        "success": True,
                        "message": "Device registered successfully in Turso",
                        "device": new_device
                    }
        
        return {"success": False, "message": "Failed to register device"}
        
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/health-metrics/")
def add_health_metric(data: HealthMetricCreate):
    try:
        # First create a device if it doesn't exist
        device_check = execute_turso_sql(f"SELECT user_id FROM devices WHERE device_id = '{data.device_id}' LIMIT 1")
        
        user_id = 1  # Default fallback
        if device_check.get("results") and len(device_check["results"]) > 0:
            response_result = device_check["results"][0].get("response", {})
            if "result" in response_result and "rows" in response_result["result"]:
                rows = response_result["result"]["rows"]
                if len(rows) > 0:
                    user_id = extract_value(rows[0][0])
                else:
                    # Device doesn't exist, create it
                    create_device_sql = f"INSERT INTO devices (device_id, user_id, model) VALUES ('{data.device_id}', 1, 'BioBand Pro')"
                    execute_turso_sql(create_device_sql)
                    user_id = 1
        
        # Insert health metric with proper NULL handling
        heart_rate_val = data.heart_rate if data.heart_rate is not None else 'NULL'
        spo2_val = data.spo2 if data.spo2 is not None else 'NULL'
        temp_val = data.temperature if data.temperature is not None else 'NULL'
        steps_val = data.steps if data.steps is not None else 'NULL'
        calories_val = data.calories if data.calories is not None else 'NULL'
        
        sql = f"INSERT INTO health_metrics (device_id, user_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp) VALUES ('{data.device_id}', {user_id}, {heart_rate_val}, {spo2_val}, {temp_val}, {steps_val}, {calories_val}, '{data.activity}', '{data.timestamp}')"
        
        insert_result = execute_turso_sql(sql)
        
        # Check if insert was successful
        if insert_result.get("results") and len(insert_result["results"]) > 0:
            result_info = insert_result["results"][0]
            if result_info.get("type") == "ok":
                # Get the newly created health metric
                get_result = execute_turso_sql("SELECT id, device_id, user_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp FROM health_metrics ORDER BY id DESC LIMIT 1")
                
                if get_result.get("results") and len(get_result["results"]) > 0:
                    response_result = get_result["results"][0].get("response", {})
                    if "result" in response_result and "rows" in response_result["result"]:
                        rows = response_result["result"]["rows"]
                        if len(rows) > 0:
                            row = rows[0]
                            health_metric = {
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
                            }
                            
                            return {
                                "success": True,
                                "message": "Health metric recorded successfully in Turso",
                                "data": health_metric
                            }
            else:
                error_msg = result_info.get("error", {}).get("message", "Unknown error")
                return {"success": False, "message": f"Database error: {error_msg}"}
        
        return {"success": False, "message": "Failed to create health metric"}
        
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

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
            "source": "Real Turso Database via HTTP"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "health_metrics": [],
            "count": 0,
            "source": "Turso Database Error"
        }

@app.get("/health-metrics/device/{device_id}")
def get_device_health_metrics(device_id: str):
    try:
        result = execute_turso_sql(
            "SELECT id, device_id, user_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp FROM health_metrics WHERE device_id = ? ORDER BY timestamp DESC",
            [device_id]
        )
        
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
            "device_id": device_id,
            "health_metrics": health_data,
            "count": len(health_data),
            "source": "Real Turso Database via HTTP"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "device_id": device_id,
            "health_metrics": [],
            "count": 0,
            "source": "Turso Database Error"
        }

@app.post("/chat/")
def health_chat(request: ChatMessage):
    """AI Health Assistant - Get medical advice and health information"""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "dummy_key":
        return {"error": "AI service not available"}
    
    # Store user message in Turso database
    try:
        user_msg_sql = f"INSERT INTO chat_messages (session_id, role, message, timestamp) VALUES ('{request.session_id}', 'user', '{request.message.replace("'", "''")}', '{datetime.now().isoformat()}')"
        execute_turso_sql(user_msg_sql)
    except Exception as e:
        print(f"Error storing user message: {e}")
    
    # Health-focused AI prompt
    health_prompt = f"""You are Bio Band AI Assistant, a health advisor for Bio Band users. You help with health questions only. Use simple English words that anyone can understand.
    
    IMPORTANT: If the question is NOT about health (like math, games, movies, etc.), say EXACTLY: "I can only help with health-related questions."
    
    For health questions:
    - Give simple, helpful advice
    - Use everyday words
    - Keep answers short and clear
    - Tell them to see a doctor for serious problems
    
    Previous chat: {user_sessions[user_session_key][-3:] if len(user_sessions[user_session_key]) > 1 else []}
    
    Question: {request.message}
    
    Remember: Only health questions. Use simple words. Keep it short."""
    
    try:
        response = requests.post(
            GEMINI_API_URL,
            headers={
                "Content-Type": "application/json",
                "X-goog-api-key": GEMINI_API_KEY,
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
            
            # Store AI response in Turso database
            try:
                ai_msg_sql = f"INSERT INTO chat_messages (session_id, role, message, timestamp) VALUES ('{request.session_id}', 'assistant', '{ai_response.replace("'", "''")}', '{datetime.now().isoformat()}')"
                execute_turso_sql(ai_msg_sql)
            except Exception as e:
                print(f"Error storing AI message: {e}")
            
            return {
                "success": True,
                "response": ai_response.strip(),
                "session_id": request.session_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"success": False, "error": f"AI API Error: {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": f"AI Error: {str(e)}"}

@app.get("/chat/{session_id}")
def get_chat_history(session_id: str):
    """Get chat history for a session from Turso database"""
    try:
        result = execute_turso_sql(f"SELECT role, message, timestamp FROM chat_messages WHERE session_id = '{session_id}' ORDER BY timestamp ASC")
        
        chat_history = []
        if result.get("results") and len(result["results"]) > 0:
            response_result = result["results"][0].get("response", {})
            if "result" in response_result and "rows" in response_result["result"]:
                rows = response_result["result"]["rows"]
                for row in rows:
                    chat_history.append({
                        "role": extract_value(row[0]),
                        "message": extract_value(row[1]),
                        "timestamp": extract_value(row[2])
                    })
        
        return {
            "success": True,
            "session_id": session_id,
            "history": chat_history,
            "message_count": len(chat_history)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "session_id": session_id,
            "history": [],
            "message_count": 0
        }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "database": "Normalized Schema"}