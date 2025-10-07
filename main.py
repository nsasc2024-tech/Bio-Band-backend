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
    heart_rate: Optional[int] = None  # Valid: 30-220 BPM
    spo2: Optional[int] = None        # Valid: 70-100%
    temperature: Optional[float] = None  # Valid: 30-45°C
    steps: Optional[int] = None       # Valid: 0-100000
    calories: Optional[int] = None    # Valid: 0-10000
    activity: Optional[str] = "Walking"

class UserCreate(BaseModel):
    full_name: str
    email: str

class DeviceCreate(BaseModel):
    device_id: str
    user_id: int
    model: str = "BioBand Pro"
    status: str = "active"

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
            "POST /devices/": "Create new device",
            "GET /health-metrics/": "Get all health data",
            "GET /health-metrics/device/{device_id}": "Get health data by device",
            "POST /health-metrics/": "Add health data (with validation)",
            "GET /health-status/{device_id}": "Get health status analysis",
            "GET /dashboard/{user_id}": "Get user dashboard with all devices",
            "GET /reports/recent/{hours}": "Get recent data report (default 24 hours)",
            "GET /reports/device/{device_id}/recent": "Get recent data report for specific device",
            "GET /reports/latest-entries/{limit}": "Get latest entries (default 10)",
            "GET /reports/recently-added/{minutes}": "Get recently added data (default 30 min)",
            "GET /reports/device-report/{device_id}": "Get complete report for specific device",
            "GET /data-validation/health-metrics": "Validate existing health data",
            "POST /data-cleanup/invalid-records": "Remove invalid health records",
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

@app.post("/devices/")
def create_device(device: DeviceCreate):
    try:
        result = execute_turso_sql(
            "INSERT INTO devices (device_id, user_id, model, status) VALUES (?, ?, ?, ?)",
            [device.device_id, device.user_id, device.model, device.status]
        )
        
        if result and result.get("results") and result["results"][0].get("type") == "ok":
            return {
                "success": True,
                "message": "Device created successfully",
                "device": {
                    "device_id": device.device_id,
                    "user_id": device.user_id,
                    "model": device.model,
                    "status": device.status
                }
            }
        
        return {"success": False, "message": "Failed to create device", "debug": result}
        
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

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
        # Validate health metrics
        validation_errors = []
        
        if data.heart_rate is not None and (data.heart_rate < 30 or data.heart_rate > 220):
            validation_errors.append(f"Invalid heart rate: {data.heart_rate} (valid range: 30-220 BPM)")
        
        if data.spo2 is not None and (data.spo2 < 70 or data.spo2 > 100):
            validation_errors.append(f"Invalid SpO2: {data.spo2} (valid range: 70-100%)")
        
        if data.temperature is not None and (data.temperature < 30.0 or data.temperature > 45.0):
            validation_errors.append(f"Invalid temperature: {data.temperature} (valid range: 30-45°C)")
        
        if data.steps is not None and (data.steps < 0 or data.steps > 100000):
            validation_errors.append(f"Invalid steps: {data.steps} (valid range: 0-100000)")
        
        if data.calories is not None and (data.calories < 0 or data.calories > 10000):
            validation_errors.append(f"Invalid calories: {data.calories} (valid range: 0-10000)")
        
        if validation_errors:
            return {"success": False, "message": "Validation failed", "errors": validation_errors}
        
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

@app.get("/health-status/{device_id}")
def get_health_status(device_id: str):
    try:
        # Get latest health metrics for the device
        result = execute_turso_sql(
            "SELECT heart_rate, spo2, temperature, steps, calories, activity, timestamp FROM health_metrics WHERE device_id = ? ORDER BY timestamp DESC LIMIT 1",
            [device_id]
        )
        
        if not (result.get("results") and result["results"][0].get("response", {}).get("result", {}).get("rows")):
            return {
                "success": False,
                "device_id": device_id,
                "status": "No data found",
                "connection_status": "disconnected"
            }
        
        row = result["results"][0]["response"]["result"]["rows"][0]
        
        # Extract values
        heart_rate = int(row[0]["value"]) if isinstance(row[0], dict) and row[0]["value"] else row[0]
        spo2 = int(row[1]["value"]) if isinstance(row[1], dict) and row[1]["value"] else row[1]
        temperature = float(row[2]["value"]) if isinstance(row[2], dict) and row[2]["value"] else row[2]
        steps = int(row[3]["value"]) if isinstance(row[3], dict) and row[3]["value"] else row[3]
        calories = int(row[4]["value"]) if isinstance(row[4], dict) and row[4]["value"] else row[4]
        activity = row[5]["value"] if isinstance(row[5], dict) else row[5]
        timestamp = row[6]["value"] if isinstance(row[6], dict) else row[6]
        
        # Analyze health status
        health_status = "Good"
        alerts = []
        
        # Heart rate analysis
        if heart_rate:
            if heart_rate < 60:
                health_status = "Low Heart Rate"
                alerts.append("Heart rate is below normal (60-100 BPM)")
            elif heart_rate > 100:
                health_status = "High Heart Rate"
                alerts.append("Heart rate is above normal (60-100 BPM)")
        
        # SpO2 analysis
        if spo2:
            if spo2 < 95:
                health_status = "Low Oxygen"
                alerts.append("Blood oxygen level is below normal (95-100%)")
        
        # Temperature analysis
        if temperature:
            if temperature > 37.5:
                health_status = "Fever"
                alerts.append("Body temperature is elevated (normal: 36-37°C)")
            elif temperature < 35.5:
                health_status = "Low Temperature"
                alerts.append("Body temperature is below normal")
        
        # Connection status (if data is recent)
        from datetime import datetime, timedelta
        try:
            last_update = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_diff = datetime.now().replace(tzinfo=last_update.tzinfo) - last_update
            connection_status = "connected" if time_diff < timedelta(minutes=5) else "disconnected"
        except:
            connection_status = "unknown"
        
        return {
            "success": True,
            "device_id": device_id,
            "connection_status": connection_status,
            "health_status": health_status,
            "alerts": alerts,
            "current_metrics": {
                "heart_rate": heart_rate,
                "spo2": spo2,
                "temperature": temperature,
                "steps": steps,
                "calories": calories,
                "activity": activity
            },
            "last_updated": timestamp,
            "recommendations": {
                "heart_rate": "Normal: 60-100 BPM",
                "spo2": "Normal: 95-100%",
                "temperature": "Normal: 36-37°C"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "device_id": device_id,
            "connection_status": "error"
        }

@app.get("/dashboard/{user_id}")
def get_user_dashboard(user_id: int):
    try:
        # Get user's devices
        devices_result = execute_turso_sql(
            "SELECT device_id, model, status FROM devices WHERE user_id = ?",
            [user_id]
        )
        
        dashboard_data = {
            "user_id": user_id,
            "devices": [],
            "overall_status": "Good",
            "total_steps_today": 0,
            "total_calories_today": 0
        }
        
        if devices_result.get("results") and devices_result["results"][0].get("response", {}).get("result", {}).get("rows"):
            device_rows = devices_result["results"][0]["response"]["result"]["rows"]
            
            for device_row in device_rows:
                device_id = device_row[0]["value"] if isinstance(device_row[0], dict) else device_row[0]
                model = device_row[1]["value"] if isinstance(device_row[1], dict) else device_row[1]
                status = device_row[2]["value"] if isinstance(device_row[2], dict) else device_row[2]
                
                # Get latest metrics for each device
                metrics_result = execute_turso_sql(
                    "SELECT heart_rate, spo2, temperature, steps, calories, activity, timestamp FROM health_metrics WHERE device_id = ? ORDER BY timestamp DESC LIMIT 1",
                    [device_id]
                )
                
                device_data = {
                    "device_id": device_id,
                    "model": model,
                    "status": status,
                    "connection_status": "disconnected",
                    "latest_metrics": None
                }
                
                if metrics_result.get("results") and metrics_result["results"][0].get("response", {}).get("result", {}).get("rows"):
                    metric_row = metrics_result["results"][0]["response"]["result"]["rows"][0]
                    
                    steps = int(metric_row[3]["value"]) if isinstance(metric_row[3], dict) and metric_row[3]["value"] else metric_row[3] or 0
                    calories = int(metric_row[4]["value"]) if isinstance(metric_row[4], dict) and metric_row[4]["value"] else metric_row[4] or 0
                    
                    dashboard_data["total_steps_today"] += steps
                    dashboard_data["total_calories_today"] += calories
                    
                    device_data["latest_metrics"] = {
                        "heart_rate": int(metric_row[0]["value"]) if isinstance(metric_row[0], dict) and metric_row[0]["value"] else metric_row[0],
                        "spo2": int(metric_row[1]["value"]) if isinstance(metric_row[1], dict) and metric_row[1]["value"] else metric_row[1],
                        "temperature": float(metric_row[2]["value"]) if isinstance(metric_row[2], dict) and metric_row[2]["value"] else metric_row[2],
                        "steps": steps,
                        "calories": calories,
                        "activity": metric_row[5]["value"] if isinstance(metric_row[5], dict) else metric_row[5],
                        "timestamp": metric_row[6]["value"] if isinstance(metric_row[6], dict) else metric_row[6]
                    }
                    device_data["connection_status"] = "connected"
                
                dashboard_data["devices"].append(device_data)
        
        return {"success": True, "dashboard": dashboard_data}
        
    except Exception as e:
        return {"success": False, "error": str(e), "user_id": user_id}

@app.get("/reports/recent/{hours}")
def get_recent_data_report(hours: int = 24):
    try:
        from datetime import datetime, timedelta
        
        # Calculate time threshold
        time_threshold = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        # Get recent health metrics
        health_result = execute_turso_sql(
            "SELECT device_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp FROM health_metrics WHERE timestamp >= ? ORDER BY timestamp DESC",
            [time_threshold]
        )
        
        # Get recent users
        users_result = execute_turso_sql(
            "SELECT full_name, email, created_at FROM users WHERE created_at >= ? ORDER BY created_at DESC",
            [time_threshold]
        )
        
        # Get recent devices
        devices_result = execute_turso_sql(
            "SELECT device_id, model, status, registered_at FROM devices WHERE registered_at >= ? ORDER BY registered_at DESC",
            [time_threshold]
        )
        
        report = {
            "report_period": f"Last {hours} hours",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "new_health_records": 0,
                "new_users": 0,
                "new_devices": 0,
                "total_steps": 0,
                "total_calories": 0,
                "avg_heart_rate": 0,
                "avg_spo2": 0,
                "avg_temperature": 0
            },
            "recent_health_data": [],
            "new_users": [],
            "new_devices": []
        }
        
        # Process health metrics
        if health_result.get("results") and health_result["results"][0].get("response", {}).get("result", {}).get("rows"):
            rows = health_result["results"][0]["response"]["result"]["rows"]
            
            heart_rates = []
            spo2_values = []
            temperatures = []
            
            for row in rows:
                device_id = row[0]["value"] if isinstance(row[0], dict) else row[0]
                heart_rate = int(row[1]["value"]) if isinstance(row[1], dict) and row[1]["value"] else row[1]
                spo2 = int(row[2]["value"]) if isinstance(row[2], dict) and row[2]["value"] else row[2]
                temperature = float(row[3]["value"]) if isinstance(row[3], dict) and row[3]["value"] else row[3]
                steps = int(row[4]["value"]) if isinstance(row[4], dict) and row[4]["value"] else row[4] or 0
                calories = int(row[5]["value"]) if isinstance(row[5], dict) and row[5]["value"] else row[5] or 0
                activity = row[6]["value"] if isinstance(row[6], dict) else row[6]
                timestamp = row[7]["value"] if isinstance(row[7], dict) else row[7]
                
                report["recent_health_data"].append({
                    "device_id": device_id,
                    "heart_rate": heart_rate,
                    "spo2": spo2,
                    "temperature": temperature,
                    "steps": steps,
                    "calories": calories,
                    "activity": activity,
                    "timestamp": timestamp
                })
                
                report["summary"]["total_steps"] += steps
                report["summary"]["total_calories"] += calories
                
                if heart_rate:
                    heart_rates.append(heart_rate)
                if spo2:
                    spo2_values.append(spo2)
                if temperature:
                    temperatures.append(temperature)
            
            report["summary"]["new_health_records"] = len(rows)
            report["summary"]["avg_heart_rate"] = round(sum(heart_rates) / len(heart_rates), 1) if heart_rates else 0
            report["summary"]["avg_spo2"] = round(sum(spo2_values) / len(spo2_values), 1) if spo2_values else 0
            report["summary"]["avg_temperature"] = round(sum(temperatures) / len(temperatures), 1) if temperatures else 0
        
        # Process new users
        if users_result.get("results") and users_result["results"][0].get("response", {}).get("result", {}).get("rows"):
            rows = users_result["results"][0]["response"]["result"]["rows"]
            for row in rows:
                report["new_users"].append({
                    "full_name": row[0]["value"] if isinstance(row[0], dict) else row[0],
                    "email": row[1]["value"] if isinstance(row[1], dict) else row[1],
                    "created_at": row[2]["value"] if isinstance(row[2], dict) else row[2]
                })
            report["summary"]["new_users"] = len(rows)
        
        # Process new devices
        if devices_result.get("results") and devices_result["results"][0].get("response", {}).get("result", {}).get("rows"):
            rows = devices_result["results"][0]["response"]["result"]["rows"]
            for row in rows:
                report["new_devices"].append({
                    "device_id": row[0]["value"] if isinstance(row[0], dict) else row[0],
                    "model": row[1]["value"] if isinstance(row[1], dict) else row[1],
                    "status": row[2]["value"] if isinstance(row[2], dict) else row[2],
                    "registered_at": row[3]["value"] if isinstance(row[3], dict) else row[3]
                })
            report["summary"]["new_devices"] = len(rows)
        
        return {"success": True, "report": report}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/reports/device/{device_id}/recent")
def get_device_recent_report(device_id: str, limit: int = 5):
    try:
        # Get recent health metrics for specific device
        result = execute_turso_sql(
            "SELECT id, heart_rate, spo2, temperature, steps, calories, activity, timestamp FROM health_metrics WHERE device_id = ? ORDER BY id DESC LIMIT ?",
            [device_id, limit]
        )
        
        if not (result.get("results") and result["results"][0].get("response", {}).get("result", {}).get("rows")):
            return {
                "success": False,
                "device_id": device_id,
                "message": "No recent data found for this device"
            }
        
        rows = result["results"][0]["response"]["result"]["rows"]
        
        recent_data = []
        total_steps = 0
        total_calories = 0
        heart_rates = []
        spo2_values = []
        temperatures = []
        
        for row in rows:
            record_id = row[0]["value"] if isinstance(row[0], dict) else str(row[0])
            heart_rate = int(row[1]["value"]) if isinstance(row[1], dict) and row[1]["value"] else row[1]
            spo2 = int(row[2]["value"]) if isinstance(row[2], dict) and row[2]["value"] else row[2]
            temperature = float(row[3]["value"]) if isinstance(row[3], dict) and row[3]["value"] else row[3]
            steps = int(row[4]["value"]) if isinstance(row[4], dict) and row[4]["value"] else row[4] or 0
            calories = int(row[5]["value"]) if isinstance(row[5], dict) and row[5]["value"] else row[5] or 0
            activity = row[6]["value"] if isinstance(row[6], dict) else row[6]
            timestamp = row[7]["value"] if isinstance(row[7], dict) else row[7]
            
            recent_data.append({
                "id": record_id,
                "heart_rate": heart_rate,
                "spo2": spo2,
                "temperature": temperature,
                "steps": steps,
                "calories": calories,
                "activity": activity,
                "timestamp": timestamp
            })
            
            total_steps += steps
            total_calories += calories
            
            if heart_rate:
                heart_rates.append(heart_rate)
            if spo2:
                spo2_values.append(spo2)
            if temperature:
                temperatures.append(temperature)
        
        # Calculate averages
        avg_heart_rate = round(sum(heart_rates) / len(heart_rates), 1) if heart_rates else 0
        avg_spo2 = round(sum(spo2_values) / len(spo2_values), 1) if spo2_values else 0
        avg_temperature = round(sum(temperatures) / len(temperatures), 1) if temperatures else 0
        
        # Analyze latest record for health status
        latest_record = recent_data[0] if recent_data else None
        health_status = "Good"
        alerts = []
        
        if latest_record:
            hr = latest_record["heart_rate"]
            sp = latest_record["spo2"]
            temp = latest_record["temperature"]
            
            if hr and (hr < 60 or hr > 100):
                health_status = "Abnormal Heart Rate"
                alerts.append(f"Heart rate {hr} BPM is outside normal range (60-100)")
            
            if sp and sp < 95:
                health_status = "Low Oxygen"
                alerts.append(f"SpO2 {sp}% is below normal (95-100%)")
            
            if temp and (temp > 37.5 or temp < 35.5):
                health_status = "Abnormal Temperature"
                alerts.append(f"Temperature {temp}°C is outside normal range (36-37°C)")
        
        return {
            "success": True,
            "device_id": device_id,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_records": len(recent_data),
                "total_steps": total_steps,
                "total_calories": total_calories,
                "avg_heart_rate": avg_heart_rate,
                "avg_spo2": avg_spo2,
                "avg_temperature": avg_temperature,
                "health_status": health_status,
                "alerts": alerts
            },
            "recent_records": recent_data
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "device_id": device_id
        }

@app.get("/reports/device-report/{device_id}")
def get_device_report(device_id: str):
    try:
        result = execute_turso_sql(
            "SELECT id, heart_rate, spo2, temperature, steps, calories, activity, timestamp FROM health_metrics WHERE device_id = ? ORDER BY timestamp DESC",
            [device_id]
        )
        
        if not (result.get("results") and result["results"][0].get("response", {}).get("result", {}).get("rows")):
            return {"success": False, "device_id": device_id, "message": "No data found"}
        
        rows = result["results"][0]["response"]["result"]["rows"]
        records = []
        total_steps = 0
        total_calories = 0
        heart_rates = []
        
        for row in rows:
            hr = int(row[1]["value"]) if isinstance(row[1], dict) and "value" in row[1] and row[1]["value"] else row[1]
            steps = int(row[4]["value"]) if isinstance(row[4], dict) and "value" in row[4] and row[4]["value"] else row[4] or 0
            calories = int(row[5]["value"]) if isinstance(row[5], dict) and "value" in row[5] and row[5]["value"] else row[5] or 0
            
            records.append({
                "id": row[0]["value"] if isinstance(row[0], dict) and "value" in row[0] else str(row[0]),
                "heart_rate": hr,
                "spo2": row[2]["value"] if isinstance(row[2], dict) and "value" in row[2] else row[2],
                "temperature": row[3]["value"] if isinstance(row[3], dict) and "value" in row[3] else row[3],
                "steps": steps,
                "calories": calories,
                "activity": row[6]["value"] if isinstance(row[6], dict) and "value" in row[6] else row[6],
                "timestamp": row[7]["value"] if isinstance(row[7], dict) and "value" in row[7] else row[7]
            })
            
            total_steps += steps
            total_calories += calories
            if hr: heart_rates.append(hr)
        
        return {
            "success": True,
            "device_id": device_id,
            "summary": {
                "total_records": len(records),
                "total_steps": total_steps,
                "total_calories": total_calories,
                "avg_heart_rate": round(sum(heart_rates) / len(heart_rates), 1) if heart_rates else 0
            },
            "records": records
        }
        
    except Exception as e:
        return {"success": False, "error": str(e), "device_id": device_id}

@app.get("/reports/recently-added/{minutes}")
def get_recently_added_data(minutes: int = 30):
    try:
        from datetime import datetime, timedelta
        
        # Calculate time threshold
        time_threshold = (datetime.now() - timedelta(minutes=minutes)).isoformat()
        
        # Get recently added health metrics
        result = execute_turso_sql(
            "SELECT id, device_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp FROM health_metrics WHERE timestamp >= ? ORDER BY timestamp DESC",
            [time_threshold]
        )
        
        recent_data = []
        if result.get("results") and result["results"][0].get("response", {}).get("result", {}).get("rows"):
            rows = result["results"][0]["response"]["result"]["rows"]
            
            for row in rows:
                recent_data.append({
                    "id": row[0]["value"] if isinstance(row[0], dict) else str(row[0]),
                    "device_id": row[1]["value"] if isinstance(row[1], dict) else row[1],
                    "heart_rate": row[2]["value"] if isinstance(row[2], dict) else row[2],
                    "spo2": row[3]["value"] if isinstance(row[3], dict) else row[3],
                    "temperature": row[4]["value"] if isinstance(row[4], dict) else row[4],
                    "steps": row[5]["value"] if isinstance(row[5], dict) else row[5],
                    "calories": row[6]["value"] if isinstance(row[6], dict) else row[6],
                    "activity": row[7]["value"] if isinstance(row[7], dict) else row[7],
                    "timestamp": row[8]["value"] if isinstance(row[8], dict) else row[8]
                })
        
        return {
            "success": True,
            "time_period": f"Last {minutes} minutes",
            "generated_at": datetime.now().isoformat(),
            "count": len(recent_data),
            "recently_added_data": recent_data
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/reports/latest-entries/{limit}")
def get_latest_entries(limit: int = 10):
    try:
        # Get latest health metrics
        health_result = execute_turso_sql(
            "SELECT id, device_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp FROM health_metrics ORDER BY id DESC LIMIT ?",
            [limit]
        )
        
        latest_data = {
            "generated_at": datetime.now().isoformat(),
            "limit": limit,
            "latest_health_records": []
        }
        
        if health_result.get("results") and health_result["results"][0].get("response", {}).get("result", {}).get("rows"):
            rows = health_result["results"][0]["response"]["result"]["rows"]
            
            for row in rows:
                latest_data["latest_health_records"].append({
                    "id": row[0]["value"] if isinstance(row[0], dict) else str(row[0]),
                    "device_id": row[1]["value"] if isinstance(row[1], dict) else row[1],
                    "heart_rate": row[2]["value"] if isinstance(row[2], dict) else row[2],
                    "spo2": row[3]["value"] if isinstance(row[3], dict) else row[3],
                    "temperature": row[4]["value"] if isinstance(row[4], dict) else row[4],
                    "steps": row[5]["value"] if isinstance(row[5], dict) else row[5],
                    "calories": row[6]["value"] if isinstance(row[6], dict) else row[6],
                    "activity": row[7]["value"] if isinstance(row[7], dict) else row[7],
                    "timestamp": row[8]["value"] if isinstance(row[8], dict) else row[8]
                })
        
        latest_data["count"] = len(latest_data["latest_health_records"])
        
        return {"success": True, "data": latest_data}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/data-cleanup/invalid-records")
def cleanup_invalid_data():
    try:
        # Delete records with invalid heart rate
        execute_turso_sql("DELETE FROM health_metrics WHERE heart_rate < 30 OR heart_rate > 220")
        
        # Delete records with invalid SpO2
        execute_turso_sql("DELETE FROM health_metrics WHERE spo2 < 70 OR spo2 > 100")
        
        # Delete records with invalid temperature
        execute_turso_sql("DELETE FROM health_metrics WHERE temperature < 30.0 OR temperature > 45.0")
        
        return {"success": True, "message": "Invalid health records removed"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "database": "Connected" if DATABASE_TOKEN else "Not configured"}