from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageRequest(BaseModel):
    message: str
    session_id: str = "default"

class UserCreate(BaseModel):
    full_name: str
    email: str

@app.get("/")
def root():
    return {
        "message": "Bio Band Medical API v2.0 is running",
        "status": "success"
    }

@app.post("/chat")
def chat(request: MessageRequest):
    return {
        "response": "Hello! I'm Bio Band AI Assistant.",
        "session_id": request.session_id
    }

@app.get("/users/")
def get_users():
    return {
        "success": True,
        "users": [],
        "count": 0
    }

@app.post("/users/")
def create_user(user: UserCreate):
    return {
        "success": True,
        "message": "User created successfully"
    }

@app.get("/devices/")
def get_devices():
    return {
        "success": True,
        "devices": [],
        "count": 0
    }

@app.get("/health-metrics/")
def get_health_metrics():
    return {
        "success": True,
        "health_metrics": [],
        "count": 0
    }