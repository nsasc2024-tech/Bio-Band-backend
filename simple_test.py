import requests
import json

# Simple test using curl-like approach
url = "https://bio-hand-praveen123.aws-ap-south-1.turso.io/v1/execute"
headers = {
    "Authorization": "Bearer eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicm8iLCJpYXQiOjE3NTkwODAyMTMsImlkIjoiNDcyMWI0MzItODgyYi00MTVkLWI3YzQtNWQyZjk5ZTFkODVlIiwicmlkIjoiYjM4YTdkNjctNzcwMi00OTIxLWIwOTEtZTI0ODI2MzIyNmJmIn0.i8h9_arPOgflWPMGsC5jwTOa97g3ICpr7Q1z5c-6TLCzXLU__j5UEgcSj5dc-vd_1fpv2I7Pxq4FnXDGCYSPDQ",
    "Content-Type": "application/json"
}

# Create family
data = {
    "stmt": "INSERT INTO families (family_name, family_code) VALUES ('Praveen Family', 'PRAVEEN2024') RETURNING id"
}

response = requests.post(url, headers=headers, json=data)
print("Create family response:", response.status_code, response.text)

# Get families
data2 = {
    "stmt": "SELECT * FROM families"
}

response2 = requests.post(url, headers=headers, json=data2)
print("Get families response:", response2.status_code, response2.text)