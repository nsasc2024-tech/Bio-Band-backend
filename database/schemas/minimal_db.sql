-- Minimal Database - No Foreign Keys, No Age
-- Database URL: libsql://bio-hand-praveen123.aws-ap-south-1.turso.io

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Devices Table
CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    model TEXT DEFAULT 'BioBand Pro',
    status TEXT DEFAULT 'active',
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. Health Metrics Table
CREATE TABLE IF NOT EXISTS health_metrics (
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

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_devices_user_id ON devices(user_id);
CREATE INDEX IF NOT EXISTS idx_devices_device_id ON devices(device_id);
CREATE INDEX IF NOT EXISTS idx_health_metrics_user_id ON health_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_health_metrics_device_id ON health_metrics(device_id);
CREATE INDEX IF NOT EXISTS idx_health_metrics_timestamp ON health_metrics(timestamp);

-- Sample Data
INSERT OR IGNORE INTO users (id, full_name, email) VALUES 
(1, 'John Doe', 'john.doe@example.com'),
(2, 'Jane Smith', 'jane.smith@example.com');

INSERT OR IGNORE INTO devices (id, device_id, user_id, model) VALUES 
(1, 'BAND001', 1, 'BioBand Pro'),
(2, 'BAND002', 2, 'BioBand Pro');

INSERT OR IGNORE INTO health_metrics (device_id, user_id, heart_rate, spo2, temperature, steps, calories, activity, timestamp) VALUES 
('BAND001', 1, 78, 97, 36.5, 1250, 55, 'Walking', '2025-09-16T10:30:00Z'),
('BAND002', 2, 72, 98, 36.2, 8500, 320, 'Running', '2025-09-16T09:15:00Z');