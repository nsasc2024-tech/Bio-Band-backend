from fastapi import FastAPI
from pydantic import BaseModel
from libsql_experimental import create_client

app = FastAPI()

# Turso Database Manager
class TursoManager:
    def __init__(self):
        self.db = create_client(
            url="libsql://bio-hand-praveen123.aws-ap-south-1.turso.io",
            auth_token="eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicm8iLCJpYXQiOjE3NTkwODAyMTMsImlkIjoiNDcyMWI0MzItODgyYi00MTVkLWI3YzQtNWQyZjk5ZTFkODVlIiwicmlkIjoiYjM4YTdkNjctNzcwMi00OTIxLWIwOTEtZTI0ODI2MzIyNmJmIn0.i8h9_arPOgflWPMGsC5jwTOa97g3ICpr7Q1z5c-6TLCzXLU__j5UEgcSj5dc-vd_1fpv2I7Pxq4FnXDGCYSPDQ"
        )
    
    def create_family(self, family_name, family_code):
        result = self.db.execute("INSERT INTO families (family_name, family_code) VALUES (?, ?) RETURNING id", [family_name, family_code])
        family_id = result.fetchone()[0]
        return {"id": family_id, "family_name": family_name, "family_code": family_code}
    
    def get_all_families(self):
        result = self.db.execute("SELECT * FROM families")
        return [{"id": f[0], "family_name": f[1], "family_code": f[2], "created_at": f[3]} for f in result.fetchall()]

db_manager = TursoManager()

# Pydantic models
class FamilyCreate(BaseModel):
    family_name: str
    family_code: str

@app.get("/")
def root():
    return {
        "message": "Bio Hand API with Family Features - Working!",
        "endpoints": {
            "POST /families/": "Create family",
            "GET /families/all": "Get all families"
        }
    }

@app.post("/families/")
def create_family(family: FamilyCreate):
    return db_manager.create_family(family.family_name, family.family_code)

@app.get("/families/all")
def get_all_families():
    return db_manager.get_all_families()

# Vercel handler
handler = app