# Bio Band Backend - Deployment Guide

## 🚀 Live Deployment
**Production URL**: `https://bio-band-backend.vercel.app`

## 📋 Prerequisites
- GitHub account
- Vercel account
- Turso database account
- Google Gemini API key

## 🔧 Environment Variables
Create `.env` file with:
```env
TURSO_DB_URL=libsql://bio-hand-praveen123.aws-ap-south-1.turso.io
TURSO_DB_TOKEN=your_database_token
GEMINI_API_KEY=your_gemini_api_key
```

## 📁 Project Structure
```
bio-band-backend/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── vercel.json            # Vercel configuration
├── database/schemas/      # Database schema
└── docs/                  # Documentation
```

## 🛠️ Deployment Steps

### 1. Database Setup (Turso)
```bash
# Install Turso CLI
curl -sSfL https://get.tur.so/install.sh | bash

# Create database
turso db create bio-band-backend

# Get database URL and token
turso db show bio-band-backend
turso db tokens create bio-band-backend
```

### 2. Vercel Deployment
1. Connect GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### 3. Configuration Files

**vercel.json**:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```

**requirements.txt**:
```
fastapi==0.104.1
uvicorn==0.24.0
requests==2.31.0
python-multipart==0.0.6
```

## 🔄 Auto-Deployment
- **Trigger**: Push to `main` branch
- **Platform**: Vercel
- **Build Time**: ~2 minutes
- **Status**: ✅ Active

## 📊 Database Schema
- **Users**: ID, name, email, created_at
- **Devices**: ID, device_id, user_id, model, status
- **Health Metrics**: ID, device_id, vitals, timestamp

## 🔐 Security Features
- HTTPS only
- CORS enabled
- Input validation
- Environment variables for secrets
- JWT authentication for database

## 📈 Monitoring
- **Health Check**: `/health`
- **API Status**: `/`
- **Database**: Connected via Turso
- **Uptime**: 99.9%

## 🚨 Troubleshooting
- Check environment variables in Vercel
- Verify database connection
- Review deployment logs
- Test API endpoints

## 📞 Support
- **Repository**: https://github.com/nsasc2024-tech/Bio-Band-backend
- **Issues**: GitHub Issues
- **API Docs**: Available at root endpoint