"""
Utility helper functions for Bio Band Backend
"""
from datetime import datetime
from typing import Any, Dict, List

def extract_turso_value(item: Any) -> Any:
    """Extract value from Turso response format"""
    return item.get('value') if isinstance(item, dict) else item

def format_response(success: bool, message: str, data: Any = None) -> Dict:
    """Standard API response format"""
    response = {
        "success": success,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    if data is not None:
        response["data"] = data
    return response

def validate_email(email: str) -> bool:
    """Basic email validation"""
    return "@" in email and "." in email.split("@")[1]

def sanitize_sql_string(value: str) -> str:
    """Sanitize string for SQL injection prevention"""
    return value.replace("'", "''") if isinstance(value, str) else str(value)