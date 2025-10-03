from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    full_name: str
    email: str

class User(BaseModel):
    id: int
    full_name: str
    email: str
    created_at: str

class UserResponse(BaseModel):
    success: bool
    message: str
    user: Optional[User] = None