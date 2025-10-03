import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("TURSO_DB_URL")
DATABASE_TOKEN = os.getenv("TURSO_DB_TOKEN")

def create_chat_table():
    headers = {
        "Authorization": f"Bearer {DATABASE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Create chat_messages table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp DATETIME NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    data = {
        "requests": [
            {
                "type": "execute",
                "stmt": {"sql": create_table_sql}
            }
        ]
    }
    
    try:
        response = requests.post(f"{DATABASE_URL}/v2/pipeline", headers=headers, json=data)
        if response.status_code == 200:
            print("Chat messages table created successfully!")
            
            # Create index for better performance
            index_sql = "CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_messages(session_id)"
            index_data = {
                "requests": [
                    {
                        "type": "execute",
                        "stmt": {"sql": index_sql}
                    }
                ]
            }
            
            index_response = requests.post(f"{DATABASE_URL}/v2/pipeline", headers=headers, json=index_data)
            if index_response.status_code == 200:
                print("Chat index created successfully!")
            else:
                print(f"Index creation failed: {index_response.text}")
        else:
            print(f"Table creation failed: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_chat_table()