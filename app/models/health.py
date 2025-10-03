from pydantic import BaseModel
from typing import Optional

class HealthMetricCreate(BaseModel):
    device_id: str
    timestamp: str
    heart_rate: Optional[int] = None
    spo2: Optional[int] = None
    temperature: Optional[float] = None
    steps: Optional[int] = None
    calories: Optional[int] = None
    activity: Optional[str] = "Walking"

class HealthMetric(BaseModel):
    id: int
    device_id: str
    user_id: int
    heart_rate: Optional[int]
    spo2: Optional[int]
    temperature: Optional[float]
    steps: Optional[int]
    calories: Optional[int]
    activity: Optional[str]
    timestamp: str

class HealthMetricResponse(BaseModel):
    success: bool
    message: str
    data: Optional[HealthMetric] = None