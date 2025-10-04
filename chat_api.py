from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = FastAPI(title="Bio Band AI Health Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

class MessageRequest(BaseModel):
    message: str
    session_id: str = "default"

API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

sessions = {}

@app.post("/chat")
async def chat(request: MessageRequest):
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
            API_URL,
            headers={
                "Content-Type": "application/json",
                "X-goog-api-key": API_KEY,
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

@app.get("/")
async def root():
    return {
        "message": "Bio Band AI Health Assistant",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "POST /chat": "Send health questions to AI",
            "GET /chat/{session_id}": "Get chat history"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)