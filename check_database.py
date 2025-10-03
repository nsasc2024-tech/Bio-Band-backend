import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

VERCEL_URL = "https://test-r67r5fcnw-praveens-projects-79540d8d.vercel.app"

def check_users():
    response = requests.get(f"{VERCEL_URL}/users/")
    data = response.json()
    
    print("Current users in database:")
    for user in data['users']:
        print(f"ID: {user['id']}, Name: {user['full_name']}, Email: {user['email']}")
    
    print(f"\nTotal users: {data['count']}")

if __name__ == "__main__":
    check_users()