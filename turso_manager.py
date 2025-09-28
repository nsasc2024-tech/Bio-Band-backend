import os
import libsql_experimental

class TursoManager:
    def __init__(self):
        self.db = libsql_experimental.connect(
            url=os.getenv("TURSO_DB_URL"),
            auth_token=os.getenv("TURSO_DB_TOKEN")
        )
        self.init_database()
    
    def init_database(self):
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT UNIQUE NOT NULL,
                user_id INTEGER,
                model TEXT,
                registered_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        self.db.execute('''
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
    
    def create_family(self, family_name, family_code):
        result = self.db.execute("INSERT INTO families (family_name, family_code) VALUES (?, ?) RETURNING id", [family_name, family_code])
        family_id = result.fetchone()[0]
        return {"id": family_id, "family_name": family_name, "family_code": family_code}
    
    def get_all_families(self):
        result = self.db.execute("SELECT * FROM families")
        return [{"id": f[0], "family_name": f[1], "family_code": f[2], "created_at": f[3]} for f in result.fetchall()]
    
    def get_family_members(self, family_id):
        result = self.db.execute("SELECT * FROM users WHERE family_id = ?", [family_id])
        return [{"id": u[0], "full_name": u[1], "email": u[2], "family_id": u[3], "role": u[4], "created_at": u[5]} for u in result.fetchall()]
    
    def create_family_invitation(self, family_id, email):
        result = self.db.execute("INSERT INTO family_invitations (family_id, email) VALUES (?, ?) RETURNING id", [family_id, email])
        invite_id = result.fetchone()[0]
        return {"id": invite_id, "family_id": family_id, "email": email, "status": "pending"}
    
    def get_user_invitations(self, email):
        result = self.db.execute("SELECT * FROM family_invitations WHERE email = ? AND status = 'pending'", [email])
        return [{"id": i[0], "family_id": i[1], "email": i[2], "status": i[3], "created_at": i[4]} for i in result.fetchall()]
    
    def create_user(self, full_name, email, family_id=None, role="member"):
        result = self.db.execute("INSERT INTO users (full_name, email, family_id, role) VALUES (?, ?, ?, ?) RETURNING id", [full_name, email, family_id, role])
        user_id = result.fetchone()[0]
        return {"id": user_id, "full_name": full_name, "email": email, "family_id": family_id, "role": role}
    
    def get_all_users(self):
        result = self.db.execute("SELECT * FROM users")
        return [{"id": u[0], "full_name": u[1], "email": u[2], "family_id": u[3], "role": u[4], "created_at": u[5]} for u in result.fetchall()]
    
    def create_device(self, device_id, user_id, model):
        self.db.execute("INSERT INTO devices (device_id, user_id, model) VALUES (?, ?, ?)", [device_id, user_id, model])
        return {"device_id": device_id, "user_id": user_id, "model": model}
    
    def get_all_devices(self):
        result = self.db.execute("SELECT * FROM devices")
        return [{"id": d[0], "device_id": d[1], "user_id": d[2], "model": d[3], "registered_at": d[4]} for d in result.fetchall()]
    
    def add_device_data(self, device_id, heart_rate=None, spo2=None, temperature=None, steps=None, calories=None, activity=None):
        self.db.execute("""
            INSERT INTO device_data (device_id, heart_rate, spo2, temperature, steps, calories, activity) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [device_id, heart_rate, spo2, temperature, steps, calories, activity])
        return {"device_id": device_id, "heart_rate": heart_rate, "spo2": spo2, "temperature": temperature, "steps": steps, "calories": calories, "activity": activity}
    
    def get_all_device_data(self):
        result = self.db.execute("SELECT * FROM device_data")
        return [{"id": d[0], "device_id": d[1], "heart_rate": d[2], "spo2": d[3], "temperature": d[4], "steps": d[5], "calories": d[6], "activity": d[7], "timestamp": d[8]} for d in result.fetchall()]
    
    def get_latest_device_data(self, device_id):
        result = self.db.execute("SELECT * FROM device_data WHERE device_id = ? ORDER BY timestamp DESC LIMIT 1", [device_id])
        data = result.fetchone()
        if data:
            return {"id": data[0], "device_id": data[1], "heart_rate": data[2], "spo2": data[3], "temperature": data[4], "steps": data[5], "calories": data[6], "activity": data[7], "timestamp": data[8]}
        return None
    
    def get_device_data(self, device_id):
        result = self.db.execute("SELECT * FROM device_data WHERE device_id = ? ORDER BY timestamp DESC", [device_id])
        return [{"id": d[0], "device_id": d[1], "heart_rate": d[2], "spo2": d[3], "temperature": d[4], "steps": d[5], "calories": d[6], "activity": d[7], "timestamp": d[8]} for d in result.fetchall()]

turso_manager = TursoManager()