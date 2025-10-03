#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("TURSO_DB_URL")
DATABASE_TOKEN = os.getenv("TURSO_DB_TOKEN")

print(f"Original URL: {DATABASE_URL}")
print(f"Token exists: {bool(DATABASE_TOKEN)}")

# Convert libsql:// URL to https:// for HTTP API
if DATABASE_URL and DATABASE_URL.startswith("libsql://"):
    DATABASE_URL = DATABASE_URL.replace("libsql://", "https://")
    print(f"Converted URL: {DATABASE_URL}")

print(f"Final URL for API: {DATABASE_URL}/v2/pipeline")