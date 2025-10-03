from pydantic import BaseModel
from typing import Optional

class DeviceCreate(BaseModel):
    device_id: str
    user_id: int
    model: str = "BioBand Pro"

class Device(BaseModel):
    id: int
    device_id: str
    user_id: int
    model: str
    status: str
    registered_at: str

class DeviceResponse(BaseModel):
    success: bool
    message: str
    device: Optional[Device] = None