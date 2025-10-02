from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class HealthMetricCreate(BaseModel):
    device_id: str
    timestamp: Optional[str] = None
    heart_rate: Optional[int] = None
    spo2: Optional[int] = None
    temperature: Optional[float] = None
    steps: Optional[int] = None
    calories: Optional[int] = None
    activity: Optional[str] = "Walking"

class UserCreate(BaseModel):
    full_name: str
    email: str
    age: Optional[int] = None
    phone: Optional[str] = None

class DeviceCreate(BaseModel):
    device_id: str
    user_id: int
    model_name: str
    device_type: Optional[str] = "smartwatch"