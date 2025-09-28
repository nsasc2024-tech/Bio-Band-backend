from fastapi import FastAPI
from pydantic import BaseModel
import os
from libsql_experimental import create_client

app = FastAPI()

# Database connection
db = create_client(
    url="libsql://bio-hand-praveen123.aws-ap-south-1.turso.io",
    auth_token="eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicm8iLCJpYXQiOjE3NTkwODAyMTMsImlkIjoiNDcyMWI0MzItODgyYi00MTVkLWI3YzQtNWQyZjk5ZTFkODVlIiwicmlkIjoiYjM4YTdkNjctNzcwMi00OTIxLWIwOTEtZTI0ODI2MzIyNmJmIn0.i8h9_arPOgflWPMGsC5jwTOa97g3ICpr7Q1z5c-6TLCzXLU__j5UEgcSj5dc-vd_1fpv2I7Pxq4FnXDGCYSPDQ"
)

class FamilyCreate(BaseModel):
    family_name: str
    family_code: str

@app.get("/")
def root():
    return {"message": "Bio Hand Family API", "status": "working"}

@app.post("/families/")
def create_family(family: FamilyCreate):
    try:
        result = db.execute(
            "INSERT INTO families (family_name, family_code) VALUES (?, ?) RETURNING id", 
            [family.family_name, family.family_code]
        )
        family_id = result.fetchone()[0]
        return {
            "success": True,
            "id": family_id, 
            "family_name": family.family_name, 
            "family_code": family.family_code
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/families/all")
def get_all_families():
    try:
        result = db.execute("SELECT * FROM families")
        families = []
        for f in result.fetchall():
            families.append({
                "id": f[0], 
                "family_name": f[1], 
                "family_code": f[2], 
                "created_at": f[3]
            })
        return {"success": True, "families": families}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)