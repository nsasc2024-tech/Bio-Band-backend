# Bio Band Health Monitoring API Documentation

**Base URL:** `https://bio-band-backend.vercel.app`

**Database:** Turso (LibSQL) - Real-time edge database

---

## 📋 API Endpoints Overview

| Method | Endpoint | Description | Status |
|--------|----------|-------------|---------|
| GET | `/` | API status and documentation | ✅ Live |
| GET | `/users/` | Get all users | ✅ Live |
| POST | `/users/` | Create new user | ✅ Live |
| GET | `/devices/` | Get all devices | ✅ Live |
| POST | `/devices/` | Register new device | ✅ Live |
| GET | `/health-metrics/` | Get all health data | ✅ Live |
| POST | `/health-metrics/` | Add health data | ✅ Live |
| GET | `/health-metrics/device/{device_id}` | Get device-specific health data | ✅ Live |
| GET | `/health` | Health check | ✅ Live |
| POST | `/chat/` | AI Health Assistant | ✅ Live |
| GET | `/chat/{session_id}` | Get chat history | ✅ Live |

---

## 🔍 Detailed API Reference

### 1. API Status
```http
GET /
```

**Response:**
```json
{
  "message": "Bio Band Health Monitoring API",
  "status": "success",
  "version": "4.0.0 - AI Enabled",
  "database_url": "libsql://bioband-praveencoder2007.aws-ap-south-1.turso.io",
  "endpoints": {
    "GET /users/": "Get all users from Turso",
    "GET /devices/": "Get all devices from Turso",
    "GET /health-metrics/": "Get all health data from Turso",
    "POST /users/": "Create user",
    "POST /devices/": "Register device",
    "POST /health-metrics/": "Add health data",
    "POST /chat/": "AI Health Assistant",
    "GET /chat/{session_id}": "Get chat history"
  }
}
```

---

## 👥 User Management

### 2. Get All Users
```http
GET /users/
```

**Response:**
```json
{
  "success": true,
  "users": [
    {
      "id": "1",
      "full_name": "John Doe",
      "email": "john.doe@example.com",
      "created_at": "2025-10-02 13:50:29"
    }
  ],
  "count": 1,
  "source": "Real Turso Database via HTTP"
}
```

### 3. Create User
```http
POST /users/
Content-Type: application/json
```

**Request Body:**
```json
{
  "full_name": "John Doe",
  "email": "john.doe@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User created successfully in Turso",
  "user": {
    "id": "8",
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "created_at": "2025-10-02 15:30:00"
  }
}
```

---

## 📱 Device Management

### 4. Get All Devices
```http
GET /devices/
```

**Response:**
```json
{
  "success": true,
  "devices": [
    {
      "id": "1",
      "device_id": "BAND001",
      "user_id": "1",
      "model": "BioBand Pro",
      "status": "active",
      "registered_at": "2025-10-02 13:50:29"
    }
  ],
  "count": 1,
  "source": "Real Turso Database via HTTP"
}
```

### 5. Register Device
```http
POST /devices/
Content-Type: application/json
```

**Request Body:**
```json
{
  "device_id": "BAND003",
  "user_id": 1,
  "model": "BioBand Pro"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Device registered successfully in Turso",
  "device": {
    "id": "3",
    "device_id": "BAND003",
    "user_id": "1",
    "model": "BioBand Pro",
    "status": "active",
    "registered_at": "2025-10-02 15:30:00"
  }
}
```

---

## 📊 Health Data Management

### 6. Get All Health Metrics
```http
GET /health-metrics/
```

**Response:**
```json
{
  "success": true,
  "health_metrics": [
    {
      "id": "1",
      "device_id": "BAND001",
      "user_id": "1",
      "heart_rate": "78",
      "spo2": "97",
      "temperature": "36.5",
      "steps": "1250",
      "calories": "55",
      "activity": "Walking",
      "timestamp": "2025-10-02T10:30:00Z"
    }
  ],
  "count": 1,
  "source": "Real Turso Database via HTTP"
}
```

### 7. Add Health Data
```http
POST /health-metrics/
Content-Type: application/json
```

**Request Body:**
```json
{
  "device_id": "BAND001",
  "timestamp": "2025-10-02T10:30:00Z",
  "heart_rate": 78,
  "spo2": 97,
  "temperature": 36.5,
  "steps": 1250,
  "calories": 55,
  "activity": "Walking"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Health metric recorded successfully in Turso",
  "data": {
    "id": "1",
    "device_id": "BAND001",
    "user_id": "1",
    "heart_rate": "78",
    "spo2": "97",
    "temperature": "36.5",
    "steps": "1250",
    "calories": "55",
    "activity": "Walking",
    "timestamp": "2025-10-02T10:30:00Z"
  }
}
```

### 8. Get Device-Specific Health Data
```http
GET /health-metrics/device/{device_id}
```

**Example:**
```http
GET /health-metrics/device/BAND001
```

**Response:**
```json
{
  "success": true,
  "device_id": "BAND001",
  "health_metrics": [
    {
      "id": "1",
      "device_id": "BAND001",
      "user_id": "1",
      "heart_rate": "78",
      "spo2": "97",
      "temperature": "36.5",
      "steps": "1250",
      "calories": "55",
      "activity": "Walking",
      "timestamp": "2025-10-02T10:30:00Z"
    }
  ],
  "count": 1,
  "source": "Real Turso Database via HTTP"
}
```

---

## 🏥 System Health

### 9. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-02T15:30:00.123456",
  "database": "Normalized Schema"
}
```

---

## 🔧 Testing with cURL

### Create User
```bash
curl -X POST https://bio-band-backend.vercel.app/users/ \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Test User", "email": "test@example.com"}'
```

### Get Users
```bash
curl https://bio-band-backend.vercel.app/users/
```

### Register Device
```bash
curl -X POST https://bio-band-backend.vercel.app/devices/ \
  -H "Content-Type: application/json" \
  -d '{"device_id": "BAND003", "user_id": 1, "model": "BioBand Pro"}'
```

### Add Health Data
```bash
curl -X POST https://bio-band-backend.vercel.app/health-metrics/ \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "BAND001",
    "timestamp": "2025-10-02T10:30:00Z",
    "heart_rate": 78,
    "spo2": 97,
    "temperature": 36.5,
    "steps": 1250,
    "calories": 55,
    "activity": "Walking"
  }'
```

---

## 📋 Data Models

### User Model
```json
{
  "id": "integer (auto-increment)",
  "full_name": "string (required)",
  "email": "string (required, unique)",
  "created_at": "datetime (auto-generated)"
}
```

### Device Model
```json
{
  "id": "integer (auto-increment)",
  "device_id": "string (required, unique)",
  "user_id": "integer (required)",
  "model": "string (default: 'BioBand Pro')",
  "status": "string (default: 'active')",
  "registered_at": "datetime (auto-generated)"
}
```

### Health Metric Model
```json
{
  "id": "integer (auto-increment)",
  "device_id": "string (required)",
  "user_id": "integer (required)",
  "heart_rate": "integer (optional)",
  "spo2": "integer (optional)",
  "temperature": "float (optional)",
  "steps": "integer (optional)",
  "calories": "integer (optional)",
  "activity": "string (optional, default: 'Walking')",
  "timestamp": "datetime (required)"
}
```

---

## 🚨 Error Responses

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error message"
}
```

---

## 🔐 Authentication
Currently, the API is open (no authentication required). For production use, implement:
- JWT tokens
- API keys
- Rate limiting

---

## 📈 Database Status
- **Database**: Turso (LibSQL)
- **Connection**: Real-time HTTP API
- **Current Records**: 
  - Users: 5
  - Devices: 2
  - Health Metrics: 0

---

## 🛠️ Technical Details
- **Framework**: FastAPI (Python)
- **Database**: Turso (Edge SQLite)
- **Deployment**: Vercel (Serverless)
- **CORS**: Enabled for all origins
- **Response Format**: JSON
- **Status Codes**: Standard HTTP codes

---

## 📞 Support
For issues or questions, check the API status endpoint or review the error messages in responses.