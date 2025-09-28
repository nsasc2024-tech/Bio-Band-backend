from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from turso_manager import turso_manager as db_manager

app = FastAPI()

@app.get("/")
def root():
    return {
        "message": "Health Monitoring API with Family Features",
        "endpoints": {
            "POST /families/": "Create family",
            "GET /families/all": "Get all families",
            "GET /families/{family_id}/members": "Get family members",
            "POST /families/invite": "Invite to family",
            "GET /families/invitations/{email}": "Get user invitations",
            "POST /users/": "Create user",
            "GET /users/all": "Get all users",
            "POST /devices/": "Register device",
            "GET /devices/all": "Get all devices",
            "POST /device-data/": "Add device data",
            "GET /device-data/all": "Get all device data",
            "GET /device-data/latest/{device_id}": "Get latest data for device",
            "GET /device-data/{device_id}": "Get all data for device"
        }
    }

# Pydantic models
class FamilyCreate(BaseModel):
    family_name: str
    family_code: str

class UserCreate(BaseModel):
    full_name: str
    email: str
    family_id: Optional[int] = None
    role: Optional[str] = "member"

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

class FamilyInvite(BaseModel):
    family_id: int
    email: str

# Family endpoints
@app.post("/families/")
def create_family(family: FamilyCreate):
    return db_manager.create_family(family.family_name, family.family_code)

@app.get("/families/all")
def get_all_families():
    return db_manager.get_all_families()

@app.get("/families/{family_id}/members")
def get_family_members(family_id: int):
    return db_manager.get_family_members(family_id)

@app.post("/families/invite")
def invite_to_family(invite: FamilyInvite):
    return db_manager.create_family_invitation(invite.family_id, invite.email)

@app.get("/families/invitations/{email}")
def get_user_invitations(email: str):
    return db_manager.get_user_invitations(email)

# User endpoints
@app.get("/users/all")
def get_all_users():
    return db_manager.get_all_users()

@app.post("/users/")
def create_user(user: UserCreate):
    return db_manager.create_user(user.full_name, user.email, user.family_id, user.role)

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
    families = db_manager.get_all_families()
    users = db_manager.get_all_users()
    devices = db_manager.get_all_devices()
    device_data = db_manager.get_all_device_data()
    
    return {
        "families": families,
        "users": users,
        "devices": devices,
        "device_data": device_data,
        "counts": {
            "families": len(families),
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