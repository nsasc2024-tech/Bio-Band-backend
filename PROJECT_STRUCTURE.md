# Bio Band Backend - Project Structure

```
bio-band-backend/
├── app/                          # Main application code
│   ├── __init__.py
│   ├── api/                      # API route handlers
│   │   └── __init__.py
│   ├── models/                   # Pydantic data models
│   │   ├── __init__.py
│   │   ├── user.py              # User models
│   │   ├── device.py            # Device models
│   │   ├── health.py            # Health metric models
│   │   └── chat.py              # Chat models
│   └── services/                 # Business logic services
│       ├── __init__.py
│       ├── database.py          # Database operations
│       └── ai_service.py        # AI/Gemini integration
│
├── config/                       # Configuration files
│   ├── __init__.py
│   ├── settings.py              # App settings and environment variables
│   ├── database/                # Database configurations
│   └── ai/                      # AI configurations
│
├── database/                     # Database related files
│   ├── migrations/              # Database migration scripts
│   └── schemas/                 # Database schema files
│       └── minimal_db.sql       # Main database schema
│
├── docs/                        # Documentation
│   ├── README.md               # Project overview
│   ├── api/                    # API documentation
│   │   ├── API_DOCUMENTATION.md
│   │   └── AI_CHAT_DOCUMENTATION.md
│   └── deployment/             # Deployment guides
│
├── scripts/                     # Utility scripts
│   ├── setup/                  # Setup scripts
│   │   └── create_chat_table.py
│   └── testing/                # Testing scripts
│       ├── check_database.py
│       ├── check_turso_data.py
│       ├── test_health_queries.py
│       └── test_vercel_api.py
│
├── tests/                       # Test files
├── utils/                       # Utility functions
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── vercel.json                 # Vercel deployment config
├── .env                        # Environment variables
├── .gitignore                  # Git ignore rules
└── PROJECT_STRUCTURE.md        # This file
```

## 📁 Folder Descriptions

### `/app` - Main Application
- **`/api`**: FastAPI route handlers and endpoints
- **`/models`**: Pydantic models for request/response validation
- **`/services`**: Business logic and external service integrations

### `/config` - Configuration
- **`settings.py`**: Centralized configuration management
- **`/database`**: Database-specific configurations
- **`/ai`**: AI service configurations

### `/database` - Database Management
- **`/migrations`**: Database migration scripts
- **`/schemas`**: SQL schema definitions

### `/docs` - Documentation
- **`/api`**: API documentation and guides
- **`/deployment`**: Deployment instructions

### `/scripts` - Utility Scripts
- **`/setup`**: Initial setup and configuration scripts
- **`/testing`**: Testing and validation scripts

### `/tests` - Test Suite
- Unit tests
- Integration tests
- API tests

### `/utils` - Utilities
- Helper functions
- Common utilities

## 🚀 Key Files

- **`main.py`**: FastAPI application entry point
- **`requirements.txt`**: Python package dependencies
- **`vercel.json`**: Vercel deployment configuration
- **`.env`**: Environment variables (not in git)
- **`.gitignore`**: Git ignore patterns

## 📊 Current Status

✅ **Structured Organization**: Clean folder hierarchy
✅ **Separated Concerns**: Models, services, and API routes separated
✅ **Documentation**: Organized in dedicated docs folder
✅ **Scripts**: Setup and testing scripts organized
✅ **Configuration**: Centralized configuration management