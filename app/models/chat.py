from pydantic import BaseModel
from typing import Optional, List

class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    success: bool
    response: str
    session_id: str
    timestamp: str

class ChatHistory(BaseModel):
    role: str
    message: str
    timestamp: str

class ChatHistoryResponse(BaseModel):
    success: bool
    session_id: str
    history: List[ChatHistory]
    message_count: int