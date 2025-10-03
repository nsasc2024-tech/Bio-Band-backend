import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def get_ai_response(message: str, session_id: str) -> dict:
    """Get AI response from Gemini API"""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "dummy_key":
        return {"error": "AI service not available"}
    
    health_prompt = f"""You are Bio Band AI Assistant, a health advisor for Bio Band users. You help with health questions only. Use simple English words that anyone can understand.
    
    IMPORTANT: If the question is NOT about health (like math, games, movies, etc.), say EXACTLY: "I can only help with health-related questions."
    
    For health questions:
    - Give simple, helpful advice
    - Use everyday words
    - Keep answers short and clear
    - Tell them to see a doctor for serious problems
    
    Question: {message}
    
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
            
            return {
                "success": True,
                "response": ai_response.strip(),
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"success": False, "error": f"AI API Error: {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": f"AI Error: {str(e)}"}