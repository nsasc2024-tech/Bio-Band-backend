from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Optional

from models import MessageRequest, User, HealthData, Alert, HealthDataType
from database import (
    get_user, create_user, get_health_data, add_health_data, 
    get_alerts
)
from health_analyzer import analyze_health_data, get_health_recommendations

load_dotenv()

app = FastAPI(title="Bio Band Medical API", version="2.0.0", description="Complete health monitoring and AI assistant API")

# Load sample data on startup
try:
    from sample_data import load_sample_data
    load_sample_data()
    print("Sample data loaded successfully!")
except Exception as e:
    print(f"Could not load sample data: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

if not API_KEY:
    print("Warning: GEMINI_API_KEY not found. Chat functionality will be limited.")
    API_KEY = "dummy_key"

# User-specific chat sessions
user_sessions = {}

# AI Health Assistant
@app.post("/chat")
async def health_chat(request: MessageRequest):
    """AI Health Assistant - Get medical advice and health information"""
    # Create user-specific session key
    user_session_key = f"{request.session_id}"
    
    if user_session_key not in user_sessions:
        user_sessions[user_session_key] = []
    
    user_sessions[user_session_key].append({"role": "user", "message": request.message, "timestamp": datetime.now()})
    
    # Enhanced prompt for health-focused responses
    health_prompt = f"""You are Bio Band AI Assistant, a mini doctor for Bio Band users. You help with health questions only. Always use very simple English words that anyone can understand. Use short sentences. Avoid big medical words.
    
    IMPORTANT: If the question is NOT about health (like math, games, movies, etc.), say EXACTLY: "I cannot help with that, I only assist with health-related queries."
    
    For health questions:
    - Give simple, easy advice
    - Use everyday words
    - Keep answers short and clear
    - Tell them to see a doctor for serious problems
    
    Previous chat: {user_sessions[user_session_key][-3:] if len(user_sessions[user_session_key]) > 1 else []}
    
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
            user_sessions[user_session_key].append({"role": "assistant", "message": ai_response, "timestamp": datetime.now()})
            return {
                "response": ai_response.strip(),
                "session_id": request.session_id,
                "timestamp": datetime.now()
            }
        else:
            error_detail = response.text if response.text else "Unknown API error"
            return {"error": f"API Error {response.status_code}: {error_detail}"}
            
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
async def root():
    return {
        "message": "Bio Band Medical API v2.0 is running",
        "features": [
            "AI Health Assistant",
            "Health Data Tracking",
            "Real-time Alerts",
            "Health Recommendations"
        ],
        "endpoints": {
            "/chat": "POST - AI Health Assistant",
            "/chat/{session_id}": "GET - Chat History",
            "/chat/user/{user_id}": "GET - User Chat Sessions",
            "/users": "POST/GET - User Management",
            "/health-data": "POST/GET - Health Metrics",
            "/alerts": "GET - Health Alerts",
            "/recommendations": "GET - Health Recommendations",
            "/docs": "GET - API Documentation"
        }
    }

# User Management Endpoints
@app.post("/users", response_model=User)
async def create_new_user(user: User):
    """Create a new user profile"""
    existing_user = get_user(user.user_id)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return create_user(user)

@app.get("/users/{user_id}", response_model=User)
async def get_user_profile(user_id: str):
    """Get user profile by ID"""
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Health Data Endpoints
@app.post("/health-data", response_model=HealthData)
async def add_health_metric(health_data: HealthData):
    """Add new health data and analyze for alerts"""
    # Verify user exists
    user = get_user(health_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Add health data
    saved_data = add_health_data(health_data)
    
    # Analyze for alerts
    analyze_health_data(health_data.user_id, health_data)
    
    return saved_data

@app.get("/health-data/{user_id}", response_model=List[HealthData])
async def get_user_health_data(user_id: str, data_type: Optional[str] = None, limit: int = 50):
    """Get health data for a user"""
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    data = get_health_data(user_id, data_type)
    return data[:limit]

# Alerts Endpoints
@app.get("/alerts/{user_id}", response_model=List[Alert])
async def get_user_alerts(user_id: str, unread_only: bool = False):
    """Get alerts for a user"""
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return get_alerts(user_id, unread_only)

# Health Recommendations
@app.get("/recommendations/{user_id}")
async def get_user_recommendations(user_id: str):
    """Get personalized health recommendations"""
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    recent_data = get_health_data(user_id)[:10]  # Last 10 entries
    recommendations = get_health_recommendations(user_id, recent_data)
    
    return {
        "user_id": user_id,
        "recommendations": recommendations,
        "generated_at": datetime.now()
    }

@app.get("/chat/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a user session"""
    user_session_key = f"{session_id}"
    
    if user_session_key in user_sessions:
        return {
            "session_id": session_id,
            "history": user_sessions[user_session_key],
            "message_count": len(user_sessions[user_session_key])
        }
    return {"session_id": session_id, "history": [], "message_count": 0}

@app.get("/chat/user/{user_id}")
async def get_user_chat_sessions(user_id: str):
    """Get all chat sessions for a specific user"""
    user_chat_sessions = {}
    for session_key, messages in user_sessions.items():
        if session_key.startswith(user_id) or session_key == user_id:
            user_chat_sessions[session_key] = {
                "message_count": len(messages),
                "last_message": messages[-1] if messages else None
            }
    
    return {
        "user_id": user_id,
        "sessions": user_chat_sessions,
        "total_sessions": len(user_chat_sessions)
    }