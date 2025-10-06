# Bio Band Backend - Project Structure

```
bio-band-backend/
├── docs/
│   ├── api/
│   │   ├── API_DOCUMENTATION.md
│   │   └── AI_CHAT_DOCUMENTATION.md
│   └── README.md
├── database/
│   └── schemas/
│       ├── minimal_db.sql
│       └── chat_messages.sql
├── .github/
│   └── workflows/
│       └── turso-deploy.yml
├── .vercel/
│   ├── project.json
│   └── README.txt
├── main.py                     # Main FastAPI application
├── requirements.txt            # Python dependencies
├── vercel.json                # Vercel deployment config
├── .env                       # Environment variables
├── .gitignore                 # Git ignore rules
├── README.md                  # Project overview
├── DATABASE_DOCUMENTATION.md  # Complete database docs
└── PROJECT_STRUCTURE.md       # This file
```

## 📁 Directory Descriptions

### **Root Files**
- `main.py` - Main FastAPI application with all endpoints
- `requirements.txt` - Python package dependencies
- `vercel.json` - Deployment configuration
- `.env` - Environment variables (not in git)

### **docs/**
- All project documentation
- API references and guides
- Database documentation

### **database/**
- Database schemas and migration files
- SQL table definitions



## 🚀 Deployment Structure

The project is structured for easy deployment:
- **Vercel**: Uses root `main.py`
- **GitHub**: All source code in root
- **Documentation**: Organized in `docs/`
- **Database**: Schemas in `database/`

## 🔧 Development Workflow

1. **Edit**: Modify `main.py`
2. **Deploy**: Push to GitHub for auto-deployment
3. **Document**: Update docs as needed