# Bio Band Health Monitoring Backend

FastAPI backend for Bio Band health monitoring system with Turso database integration.

## 🚀 Features

- **Real-time Health Data**: Collect heart rate, SpO2, temperature, steps, calories
- **Device Management**: Register and track multiple Bio Band devices
- **User Management**: User registration and profile management
- **Turso Database**: Edge database with global distribution
- **REST API**: Complete API for frontend/mobile integration
- **Vercel Deployment**: Serverless deployment with auto-scaling

## 🏗️ Architecture

```
Hardware Band → FastAPI → Turso Database → Frontend/Mobile
```

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Devices Table
```sql
CREATE TABLE devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    model TEXT DEFAULT 'BioBand Pro',
    status TEXT DEFAULT 'active',
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Health Metrics Table
```sql
CREATE TABLE health_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    heart_rate INTEGER,
    spo2 INTEGER,
    temperature REAL,
    steps INTEGER,
    calories INTEGER,
    activity TEXT,
    timestamp DATETIME NOT NULL
);
```

## 🔧 Setup

1. **Clone Repository**
```bash
git clone <your-repo-url>
cd test
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Environment Variables**
Create `.env` file:
```
TURSO_DB_URL=your_turso_database_url
TURSO_DB_TOKEN=your_turso_auth_token
```

4. **Run Locally**
```bash
uvicorn main:app --reload
```

## 📡 API Endpoints

### GET Endpoints
- `GET /` - API documentation
- `GET /users/` - Get all users
- `GET /devices/` - Get all devices
- `GET /health-metrics/` - Get all health data
- `GET /health-metrics/device/{device_id}` - Get device-specific data
- `GET /health` - Health check

### POST Endpoints
- `POST /users/` - Create user
- `POST /devices/` - Register device
- `POST /health-metrics/` - Add health data

## 🌐 Live API

**Base URL**: `https://test-1fwwt93bt-praveens-projects-79540d8d.vercel.app`

**API Docs**: `/docs`

## 🧪 Testing

Test with curl:
```bash
# Get users
curl https://test-1fwwt93bt-praveens-projects-79540d8d.vercel.app/users/

# Create user
curl -X POST https://test-1fwwt93bt-praveens-projects-79540d8d.vercel.app/users/ \
  -H "Content-Type: application/json" \
  -d '{"full_name": "John Doe", "email": "john@example.com"}'

# Add health data
curl -X POST https://test-1fwwt93bt-praveens-projects-79540d8d.vercel.app/health-metrics/ \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "BAND001",
    "timestamp": "2025-01-23T10:30:00Z",
    "heart_rate": 78,
    "spo2": 97,
    "temperature": 36.5,
    "steps": 1250,
    "calories": 55,
    "activity": "Walking"
  }'
```

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: Turso (LibSQL)
- **Deployment**: Vercel
- **Validation**: Pydantic

## 📈 Status

✅ **Completed**
- Database schema design
- API endpoints implementation
- Turso integration
- Vercel deployment
- CORS configuration

🔄 **In Progress**
- Authentication system
- Real-time WebSocket support
- Data analytics endpoints

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

MIT License