from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
from datetime import datetime

# In-memory storage
users = []
devices = []
device_data = []

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        if path == '/users/all':
            self.wfile.write(json.dumps(users).encode())
        elif path == '/devices/all':
            self.wfile.write(json.dumps(devices).encode())
        elif path == '/device-data/all':
            self.wfile.write(json.dumps(device_data).encode())
        elif path.startswith('/device-data/latest/'):
            device_id = path.split('/')[-1]
            device_records = [d for d in device_data if d["device_id"] == device_id]
            if device_records:
                self.wfile.write(json.dumps(device_records[-1]).encode())
            else:
                self.wfile.write(json.dumps({"error": "No data found"}).encode())
        elif path.startswith('/device-data/'):
            device_id = path.split('/')[-1]
            device_records = [d for d in device_data if d["device_id"] == device_id]
            self.wfile.write(json.dumps(device_records).encode())
        else:
            response = {
                "message": "Health Monitoring API",
                "endpoints": {
                    "POST /users/": "Create user",
                    "POST /devices/": "Register device",
                    "POST /device-data/": "Add device data",
                    "GET /users/all": "Get all users",
                    "GET /devices/all": "Get all devices",
                    "GET /device-data/all": "Get all device data",
                    "GET /device-data/latest/{device_id}": "Get latest data for device",
                    "GET /device-data/{device_id}": "Get all data for device"
                }
            }
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            if content_length == 0:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error = {"error": "No data provided"}
                self.wfile.write(json.dumps(error).encode())
                return
                
            data = json.loads(post_data.decode('utf-8'))
            
            if path == '/users/':
                if not data.get("full_name") or not data.get("email"):
                    response = {"error": "full_name and email are required"}
                else:
                    user_id = len(users) + 1
                    new_user = {
                        "user_id": user_id,
                        "full_name": data.get("full_name"),
                        "email": data.get("email"),
                        "created_at": datetime.now().isoformat()
                    }
                    users.append(new_user)
                    response = new_user
            elif path == '/devices/':
                if not data.get("device_id") or not data.get("user_id") or not data.get("model"):
                    response = {"error": "device_id, user_id and model are required"}
                else:
                    new_device = {
                        "device_id": data.get("device_id"),
                        "user_id": data.get("user_id"),
                        "model": data.get("model"),
                        "registered_at": datetime.now().isoformat()
                    }
                    devices.append(new_device)
                    response = new_device
            elif path == '/device-data/':
                if not data.get("device_id"):
                    response = {"error": "device_id is required"}
                else:
                    data_id = len(device_data) + 1
                    new_data = {
                        "data_id": data_id,
                        "device_id": data.get("device_id"),
                        "timestamp": datetime.now().isoformat(),
                        "heart_rate": data.get("heart_rate"),
                        "spo2": data.get("spo2"),
                        "temperature": data.get("temperature"),
                        "steps": data.get("steps"),
                        "calories": data.get("calories"),
                        "activity": data.get("activity")
                    }
                    device_data.append(new_data)
                    response = new_data
            else:
                response = {"error": "Endpoint not found"}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error = {"error": "Invalid JSON format"}
            self.wfile.write(json.dumps(error).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error = {"error": f"Server error: {str(e)}"}
            self.wfile.write(json.dumps(error).encode())
    
