# Bio Band Backend API

**Complete backend system for Bio Band health monitoring wearable device.**

## 🚀 Live API
**Base URL**: `https://bio-band-backend.vercel.app`

## 🎯 Quick Start

### **Test API Endpoints**
```bash
# Get API status
curl https://bio-band-backend.vercel.app/

# Get all users
curl https://bio-band-backend.vercel.app/users/

# AI Health Chat
curl -X POST https://bio-band-backend.vercel.app/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I have a headache", "session_id": "test"}'
```

## 🤖 Features
- **AI Health Assistant** - Gemini-powered health advice
- **Health Data Tracking** - Store sensor data from Bio Band devices
- **User Management** - Registration and profile management
- **Device Management** - Bio Band device pairing and tracking
- **Real-time Data** - Live health metrics from wearable devices

## 🛠️ Tech Stack
- **FastAPI** - Modern Python web framework
- **Turso** - Distributed SQLite database
- **Gemini AI** - Google's advanced AI model
- **Vercel** - Serverless deployment platform

## 📊 Database
- **Turso Database** - Global edge SQLite database
- **3 Tables**: users, devices, health_metrics
- **Current Data**: 15+ users, 13+ health records
- **Real-time Storage** - Instant data synchronization

## 📱 API Endpoints

| Endpoint | Method | Description |
|----------|--------|--------------|
| `/` | GET | API status and info |
| `/users/` | GET/POST | User management |
| `/users/{id}` | GET | Get specific user |
| `/devices/` | GET/POST | Device management |
| `/health-metrics/` | GET/POST | Health data |
| `/health-metrics/device/{id}` | GET | Device-specific data |
| `/chat` | POST | AI health assistant |
| `/chat/{session_id}` | GET | Chat history |

## 📁 Project Structure

```
bio-band-backend/
├── src/main.py              # Main application
├── docs/                    # Documentation
├── database/schemas/        # Database schemas
├── main.py                  # Deployment file
├── requirements.txt         # Dependencies
└── vercel.json             # Deployment config
```

## 🔧 Local Development

```bash
# Clone repository
git clone https://github.com/nsasc2024-tech/Bio-Band-backend.git
cd Bio-Band-backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables in .env
TURSO_DB_URL=your_database_url
TURSO_DB_TOKEN=your_database_token
GEMINI_API_KEY=your_gemini_key

# Run locally
python main.py
```

## 📚 Documentation

- **[API Documentation](docs/api/API_DOCUMENTATION.md)** - Complete API reference
- **[AI Chat Guide](docs/api/AI_CHAT_DOCUMENTATION.md)** - AI assistant endpoints
- **[Database Schema](DATABASE_DOCUMENTATION.md)** - Complete database details
- **[Project Structure](PROJECT_STRUCTURE.md)** - Code organization

## 🌍 Deployment

- **Platform**: Vercel
- **Auto-deploy**: Connected to GitHub main branch
- **Environment**: Production-ready with global CDN
- **Status**: ✅ Live and operational

## 📈 Current Status

- ✅ **15+ Users** registered
- ✅ **13+ Health Records** stored
- ✅ **AI Chat** working with Gemini
- ✅ **Global Edge** database with Turso
- ✅ **Production Ready** on Vercel

## 🔐 Security

- HTTPS only
- JWT authentication for database
- CORS enabled for web/mobile apps
- Environment variables for sensitive data
- Input validation and sanitization

## 📞 Integration

Perfect for integration with:
- **Mobile Apps**: React Native, Flutter
- **Web Dashboards**: React, Vue, Angular
- **IoT Devices**: Arduino, Raspberry Pi
- **Wearable Devices**: Bio Band hardware

---

**🏥 Built for Bio Band Health Monitoring System**  
**🔗 Repository**: https://github.com/nsasc2024-tech/Bio-Band-backend  
**📊 Live API**: https://bio-band-backend.vercel.app