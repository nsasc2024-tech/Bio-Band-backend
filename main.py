from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from datetime import datetime

app = FastAPI(title="Bio Band Medical API", version="2.0.0", description="Complete health monitoring and AI assistant API")

# Turso Database
DATABASE_URL = os.getenv("TURSO_DB_URL", "")
DATABASE_TOKEN = os.getenv("TURSO_DB_TOKEN", "")

# Gemini AI
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBx4_h7kQdD_zGzIeQ9MctV45S-cwbBcXY")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

if not API_KEY or API_KEY == "dummy_key":
    print("Warning: GEMINI_API_KEY not found. Chat functionality will be limited.")
    API_KEY = "AIzaSyBx4_h7kQdD_zGzIeQ9MctV45S-cwbBcXY"



if DATABASE_URL and DATABASE_URL.startswith("libsql://"):
    DATABASE_URL = DATABASE_URL.replace("libsql://", "https://").rstrip('/')

def execute_sql(sql):
    if not DATABASE_URL or not DATABASE_TOKEN:
        return {"error": "Database not configured"}
    
    try:
        headers = {"Authorization": f"Bearer {DATABASE_TOKEN}", "Content-Type": "application/json"}
        data = {"requests": [{"type": "execute", "stmt": {"sql": sql}}]}
        url = f"{DATABASE_URL}/v2/pipeline"
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to Turso database. Check URL and network."}
    except requests.exceptions.Timeout:
        return {"error": "Database request timed out"}
    except Exception as e:
        return {"error": f"Connection failed: {str(e)}"}

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

class UserCreate(BaseModel):
    full_name: str
    email: str

class DeviceCreate(BaseModel):
    device_id: str
    user_id: int
    model: str = "BioBand Pro"

class HealthMetricCreate(BaseModel):
    device_id: str
    user_id: int
    timestamp: str
    heart_rate: int = None
    spo2: int = None
    temperature: float = None
    steps: int = None
    calories: int = None
    activity: str = "Walking"

@app.get("/")
def root():
    # Test database connection
    db_status = "connected" if DATABASE_URL and DATABASE_TOKEN else "not configured"
    if DATABASE_URL and DATABASE_TOKEN:
        test_result = execute_sql("SELECT 1")
        db_status = "working" if "error" not in test_result else f"error: {test_result['error']}"
    
    return {
        "message": "Bio Band Medical API v2.0 is running",
        "status": "success",
        "database": db_status,
        "features": [
            "AI Health Assistant",
            "Health Data Tracking",
            "User Management",
            "Device Management"
        ],
        "endpoints": {
            "/chat": "POST - AI Health Assistant",
            "/users/": "POST/GET - User Management",
            "/devices/": "POST/GET - Device Management",
            "/health-metrics/": "POST/GET - Health Metrics",
            "/docs": "GET - API Documentation"
        }
    }

@app.post("/chat")
async def health_chat(request: MessageRequest):
    """AI Health Assistant - Get medical advice and health information"""
    health_prompt = f"""You are Bio Band AI Assistant, a mini doctor for Bio Band users. You help with health questions only. Always use very simple English words that anyone can understand. Use short sentences. Avoid big medical words.
    
    IMPORTANT: If the question is NOT about health (like math, games, movies, etc.), say EXACTLY: "I cannot help with that, I only assist with health-related queries."
    
    For health questions:
    - Give simple, easy advice
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
                "generationConfig": {"maxOutputTokens": 1000}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data["candidates"][0]["content"]["parts"][0]["text"]
            return {"answer": ai_response.strip()}
        else:
            return {"error": f"API Error {response.status_code}: {response.text}"}
            
    except Exception as e:
        return {"error": str(e)}

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

@app.get("/users/{user_id}")
def get_user_by_id(user_id: int):
    try:
        result = execute_sql(f"SELECT id, full_name, email, created_at FROM users WHERE id = {user_id}")
        
        if "error" in result:
            return {"success": False, "error": result["error"]}
        
        if result.get("results") and len(result["results"]) > 0:
            response_result = result["results"][0].get("response", {})
            if "result" in response_result and "rows" in response_result["result"]:
                rows = response_result["result"]["rows"]
                if rows:
                    row = rows[0]
                    return {
                        "success": True,
                        "user": {
                            "id": extract_value(row[0]),
                            "full_name": extract_value(row[1]),
                            "email": extract_value(row[2]),
                            "created_at": extract_value(row[3])
                        }
                    }
        
        return {"success": False, "error": "User not found"}
    except:
        return {"success": False, "error": "Failed to get user"}

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

@app.get("/devices/{id}")
def get_device_by_id(id: int):
    try:
        result = execute_sql(f"SELECT id, device_id, user_id, model, status, registered_at FROM devices WHERE id = {id}")
        
        if "error" in result:
            return {"success": False, "error": result["error"]}
        
        if result.get("results") and len(result["results"]) > 0:
            response_result = result["results"][0].get("response", {})
            if "result" in response_result and "rows" in response_result["result"]:
                rows = response_result["result"]["rows"]
                if rows:
                    row = rows[0]
                    return {
                        "success": True,
                        "device": {
                            "id": extract_value(row[0]),
                            "device_id": extract_value(row[1]),
                            "user_id": extract_value(row[2]),
                            "model": extract_value(row[3]),
                            "status": extract_value(row[4]),
                            "registered_at": extract_value(row[5])
                        }
                    }
        
        return {"success": False, "error": "Device not found"}
    except:
        return {"success": False, "error": "Failed to get device"}

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
        
        sql = f"INSERT INTO health_metrics (device_id, user_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp) VALUES ('{data.device_id}', {data.user_id}, {heart_rate_val}, {spo2_val}, {temp_val}, {steps_val}, {calories_val}, '{data.activity}', '{data.timestamp}')"
        
        result = execute_sql(sql)
        
        if "error" in result:
            return {"success": False, "message": result["error"]}
        
        return {"success": True, "message": "Health metric created successfully"}
    except:
        return {"success": False, "message": "Failed to create health metric"}

@app.get("/health-metrics/{device_id}")
def get_health_metrics_by_device(device_id: str):
    try:
        result = execute_sql(f"SELECT id, device_id, user_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp FROM health_metrics WHERE device_id = '{device_id}' ORDER BY timestamp DESC")
        
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



@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(), "database": "Turso"}