import requests
import json

# Test Turso database directly using HTTP API
def test_turso_connection():
    url = "https://bio-hand-praveen123.aws-ap-south-1.turso.io/v1/execute"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicm8iLCJpYXQiOjE3NTkwODAyMTMsImlkIjoiNDcyMWI0MzItODgyYi00MTVkLWI3YzQtNWQyZjk5ZTFkODVlIiwicmlkIjoiYjM4YTdkNjctNzcwMi00OTIxLWIwOTEtZTI0ODI2MzIyNmJmIn0.i8h9_arPOgflWPMGsC5jwTOa97g3ICpr7Q1z5c-6TLCzXLU__j5UEgcSj5dc-vd_1fpv2I7Pxq4FnXDGCYSPDQ",
        "Content-Type": "application/json"
    }
    
    # Test connection
    data = {
        "statements": [
            {
                "stmt": "SELECT 1 as test"
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=data)
    print("Connection test:", response.json())
    
    # Create family
    create_family_data = {
        "statements": [
            {
                "stmt": "INSERT INTO families (family_name, family_code) VALUES (?, ?) RETURNING id",
                "args": ["Praveen Family", "PRAVEEN2024"]
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=create_family_data)
    print("Create family:", response.json())
    
    # Get all families
    get_families_data = {
        "statements": [
            {
                "stmt": "SELECT * FROM families"
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=get_families_data)
    print("All families:", response.json())

if __name__ == "__main__":
    test_turso_connection()