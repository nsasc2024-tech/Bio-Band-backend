#!/usr/bin/env python3
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def query_turso(sql):
    url = "https://bioband-nsasc2024-tech.aws-ap-south-1.turso.io/v2/pipeline"
    token = os.getenv('TURSO_DB_TOKEN')
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "requests": [
            {
                "type": "execute",
                "stmt": {
                    "sql": sql
                }
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    
    if result['results'][0]['type'] == 'ok':
        rows = result['results'][0]['response']['result']['rows']
        cols = result['results'][0]['response']['result']['cols']
        
        print(f"Found {len(rows)} users:")
        print("-" * 50)
        
        for row in rows:
            id_val = row[0]['value']
            name_val = row[1]['value']
            email_val = row[2]['value']
            created_val = row[3]['value']
            print(f"ID: {id_val} | Name: {name_val} | Email: {email_val} | Created: {created_val}")
    else:
        print(f"Error: {result['results'][0]['error']['message']}")

print("Current users in Turso database:")
query_turso("SELECT * FROM users ORDER BY id DESC;")