#!/usr/bin/env python3
import requests
import json

# Check API status to see which database it's using
response = requests.get("https://bio-band-backend.vercel.app/")
result = response.json()

print("API Database Configuration:")
print(f"Database URL: {result.get('database_url', 'Not found')}")
print(f"Version: {result.get('version', 'Not found')}")

# Check users from API
users_response = requests.get("https://bio-band-backend.vercel.app/users/")
users_data = users_response.json()

print(f"\nUsers from API: {users_data.get('count', 0)}")
if users_data.get('users'):
    latest_user = max(users_data['users'], key=lambda x: int(x['id']))
    print(f"Latest user ID: {latest_user['id']} - {latest_user['full_name']}")