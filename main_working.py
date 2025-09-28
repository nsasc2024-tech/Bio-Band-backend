from fastapi import FastAPI
from pydantic import BaseModel
import os
import requests
import json

app = FastAPI()

# Simple in-memory storage for testing
families_db = []
family_counter = 1

class FamilyCreate(BaseModel):
    family_name: str
    family_code: str

@app.get("/")
def root():
    return {
        "message": "Bio Hand API with Family Features - Working!",
        "status": "success",
        "endpoints": {
            "POST /families/": "Create family",
            "GET /families/all": "Get all families"
        }
    }

@app.post("/families/")
def create_family(family: FamilyCreate):
    global family_counter
    
    # Create family in memory
    new_family = {
        "id": family_counter,
        "family_name": family.family_name,
        "family_code": family.family_code,
        "created_at": "2024-09-28T16:00:00Z"
    }
    families_db.append(new_family)
    
    # Also try to save to Turso via HTTP API
    try:
        turso_url = "https://bio-hand-praveen123.aws-ap-south-1.turso.io/v1/execute"
        headers = {
            "Authorization": f"Bearer {os.getenv('TURSO_DB_TOKEN', 'eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicm8iLCJpYXQiOjE3NTkwODAyMTMsImlkIjoiNDcyMWI0MzItODgyYi00MTVkLWI3YzQtNWQyZjk5ZTFkODVlIiwicmlkIjoiYjM4YTdkNjctNzcwMi00OTIxLWIwOTEtZTI0ODI2MzIyNmJmIn0.i8h9_arPOgflWPMGsC5jwTOa97g3ICpr7Q1z5c-6TLCzXLU__j5UEgcSj5dc-vd_1fpv2I7Pxq4FnXDGCYSPDQ')}",
            "Content-Type": "application/json"
        }
        
        data = {
            "statements": [{
                "stmt": f"INSERT INTO families (family_name, family_code) VALUES ('{family.family_name}', '{family.family_code}')"
            }]
        }
        
        response = requests.post(turso_url, headers=headers, json=data)
        turso_success = response.status_code == 200
    except:
        turso_success = False
    
    family_counter += 1
    
    return {
        "success": True,
        "id": new_family["id"],
        "family_name": family.family_name,
        "family_code": family.family_code,
        "saved_to_turso": turso_success
    }

@app.get("/families/all")
def get_all_families():
    return {
        "success": True,
        "families": families_db,
        "count": len(families_db)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)