# Bio Band Backend - Project Structure

```
bio-band-backend/
├── src/
│   └── main.py                 # Main FastAPI application
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
├── main.py                     # Root main.py for Vercel deployment
├── requirements.txt            # Python dependencies
├── vercel.json                # Vercel deployment config
├── .env                       # Environment variables
├── .gitignore                 # Git ignore rules
├── README.md                  # Project overview
├── DATABASE_DOCUMENTATION.md  # Complete database docs
└── PROJECT_STRUCTURE.md       # This file
```

## 📁 Directory Descriptions

### **src/**
- Contains the main application code
- `main.py` - FastAPI application with all endpoints

### **docs/**
- All project documentation
- API references and guides
- Database documentation

### **database/**
- Database schemas and migration files
- SQL table definitions

### **Root Files**
- `main.py` - Copy for Vercel deployment
- `requirements.txt` - Python package dependencies
- `vercel.json` - Deployment configuration
- `.env` - Environment variables (not in git)

## 🚀 Deployment Structure

The project is structured for easy deployment:
- **Vercel**: Uses root `main.py`
- **GitHub**: Source code in `src/`
- **Documentation**: Organized in `docs/`
- **Database**: Schemas in `database/`

## 🔧 Development Workflow

1. **Edit**: Modify `src/main.py`
2. **Sync**: Copy changes to root `main.py`
3. **Deploy**: Push to GitHub for auto-deployment
4. **Document**: Update docs as needed