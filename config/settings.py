import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
TURSO_DB_URL = os.getenv("TURSO_DB_URL")
TURSO_DB_TOKEN = os.getenv("TURSO_DB_TOKEN")

# AI Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# API Configuration
API_TITLE = "Bio Band Health Monitoring API"
API_VERSION = "4.0.0 - AI Enabled"
API_DESCRIPTION = "Complete health monitoring and AI assistant API"

# CORS Configuration
CORS_ORIGINS = ["*"]
CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_HEADERS = ["*"]