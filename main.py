from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from turso_manager import turso_manager as db_manager

app = FastAPI()

@app.get("/")
def root():
    return {
        "message": "Health Monitoring API",
        "endpoints": {
            "POST /users/": "Create user",
            "POST /devices/": "Register device",
            "POST /device-data/": "Add device data",
            "GET /users/all": "Get all users",
            "GET /devices/all": "Get all devices",
            "GET /device-data/all": "Get all device data",
            "GET /device-data/latest/{device_id}": "Get latest data for device",
            "GET /device-data/{device_id}": "Get all data for device"
        }
    }

# Pydantic models
class UserCreate(BaseModel):
    full_name: str
    email: str

class DeviceCreate(BaseModel):
    device_id: str
    user_id: int
    model: str

class DeviceDataCreate(BaseModel):
    device_id: str
    heart_rate: Optional[int] = None
    spo2: Optional[int] = None
    temperature: Optional[float] = None
    steps: Optional[int] = None
    calories: Optional[int] = None
    activity: Optional[str] = None

@app.get("/users/all")
def get_all_users():
    return db_manager.get_all_users()

@app.post("/users/")
def create_user(user: UserCreate):
    return db_manager.create_user(user.full_name, user.email)

@app.get("/devices/all")
def get_all_devices():
    return db_manager.get_all_devices()

@app.post("/devices/")
def register_device(device: DeviceCreate):
    return db_manager.create_device(device.device_id, device.user_id, device.model)

@app.get("/device-data/all")
def get_all_device_data():
    return db_manager.get_all_device_data()

@app.post("/device-data/")
def add_device_data(data: DeviceDataCreate):
    return db_manager.add_device_data(
        data.device_id, data.heart_rate, data.spo2, 
        data.temperature, data.steps, data.calories, data.activity
    )

@app.get("/device-data/latest/{device_id}")
def fetch_latest_data(device_id: str):
    latest_data = db_manager.get_latest_device_data(device_id)
    if not latest_data:
        raise HTTPException(status_code=404, detail="No data found for device")
    return latest_data

@app.get("/device-data/{device_id}")
def fetch_all_data(device_id: str):
    all_data = db_manager.get_device_data(device_id)
    if not all_data:
        raise HTTPException(status_code=404, detail="No data found for device")
    return all_data

@app.get("/api/test-db")
def test_db():
    try:
        from lib.db import db
        result = db.execute("SELECT 1 as test")
        return {"connected": True, "result": result.fetchall()}
    except Exception as error:
        return {"connected": False, "error": str(error)}

@app.get("/debug/database")
def view_database():
    users = db_manager.get_all_users()
    devices = db_manager.get_all_devices()
    device_data = db_manager.get_all_device_data()
    
    return {
        "users": users,
        "devices": devices,
        "device_data": device_data,
        "counts": {
            "users": len(users),
            "devices": len(devices),
            "device_data": len(device_data)
        }
    }

# Vercel handler
handler = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)