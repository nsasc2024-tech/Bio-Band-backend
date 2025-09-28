# Database: app.db (SQLite)

# Table: users
# - id (INTEGER, PRIMARY KEY)
# - full_name (STRING)
# - email (STRING, UNIQUE)
# - created_at (DATETIME)

# Table: devices  
# - id (INTEGER, PRIMARY KEY)
# - device_id (STRING, UNIQUE)
# - user_id (INTEGER, FOREIGN KEY -> users.id)
# - model (STRING)
# - registered_at (DATETIME)

# Table: device_data
# - id (INTEGER, PRIMARY KEY)
# - device_id (STRING, FOREIGN KEY -> devices.device_id)
# - heart_rate (INTEGER)
# - spo2 (INTEGER)
# - temperature (FLOAT)
# - steps (INTEGER)
# - calories (INTEGER)
# - activity (STRING)
# - timestamp (DATETIME)