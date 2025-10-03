from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

if not API_KEY:
    print("Warning: GEMINI_API_KEY not found.")
    API_KEY = "dummy_key"

user_sessions = {}

class MessageRequest(BaseModel):
    message: str
    session_id: str = "default"

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

@app.get("/")
async def root():
    return {
        "message": "Bio Band Medical API v2.0 is running",
        "features": ["AI Health Assistant with Gemini"],
        "endpoints": {
            "/chat": "POST - Chat with Gemini AI",
            "/chat/{session_id}": "GET - Chat History"
        }
    }

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