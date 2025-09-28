import sqlite3
import json
import os
from datetime import datetime

class SQLiteManager:
    def __init__(self):
        # Use environment variable for database URL or fallback to local file
        self.db_file = os.getenv("DATABASE_URL", "app.db")
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create devices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT UNIQUE NOT NULL,
                user_id INTEGER,
                model TEXT,
                registered_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create device_data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS device_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                heart_rate INTEGER,
                spo2 INTEGER,
                temperature REAL,
                steps INTEGER,
                calories INTEGER,
                activity TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES devices (device_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, full_name, email):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (full_name, email) VALUES (?, ?)", (full_name, email))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return {"id": user_id, "full_name": full_name, "email": email}
    
    def get_all_users(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        conn.close()
        return [{"id": u[0], "full_name": u[1], "email": u[2], "created_at": u[3]} for u in users]
    
    def create_device(self, device_id, user_id, model):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO devices (device_id, user_id, model) VALUES (?, ?, ?)", (device_id, user_id, model))
        conn.commit()
        conn.close()
        return {"device_id": device_id, "user_id": user_id, "model": model}
    
    def get_all_devices(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM devices")
        devices = cursor.fetchall()
        conn.close()
        return [{"id": d[0], "device_id": d[1], "user_id": d[2], "model": d[3], "registered_at": d[4]} for d in devices]
    
    def add_device_data(self, device_id, heart_rate=None, spo2=None, temperature=None, steps=None, calories=None, activity=None):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO device_data (device_id, heart_rate, spo2, temperature, steps, calories, activity) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (device_id, heart_rate, spo2, temperature, steps, calories, activity))
        conn.commit()
        conn.close()
        return {"device_id": device_id, "heart_rate": heart_rate, "spo2": spo2, "temperature": temperature, "steps": steps, "calories": calories, "activity": activity}
    
    def get_all_device_data(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM device_data")
        data = cursor.fetchall()
        conn.close()
        return [{"id": d[0], "device_id": d[1], "heart_rate": d[2], "spo2": d[3], "temperature": d[4], "steps": d[5], "calories": d[6], "activity": d[7], "timestamp": d[8]} for d in data]
    
    def get_latest_device_data(self, device_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM device_data WHERE device_id = ? ORDER BY timestamp DESC LIMIT 1", (device_id,))
        data = cursor.fetchone()
        conn.close()
        if data:
            return {"id": data[0], "device_id": data[1], "heart_rate": data[2], "spo2": data[3], "temperature": data[4], "steps": data[5], "calories": data[6], "activity": data[7], "timestamp": data[8]}
        return None
    
    def get_device_data(self, device_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM device_data WHERE device_id = ? ORDER BY timestamp DESC", (device_id,))
        data = cursor.fetchall()
        conn.close()
        return [{"id": d[0], "device_id": d[1], "heart_rate": d[2], "spo2": d[3], "temperature": d[4], "steps": d[5], "calories": d[6], "activity": d[7], "timestamp": d[8]} for d in data]

# Global instance
db_manager = SQLiteManager()