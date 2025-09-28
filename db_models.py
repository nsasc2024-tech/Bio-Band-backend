from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Database setup
SQLALCHEMY_DATABASE_URL = 'sqlite:///./app.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Table Models
class AppUser(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    devices = relationship("UserDevice", back_populates="user")

class UserDevice(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    model = Column(String)
    registered_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("AppUser", back_populates="devices")
    data = relationship("DeviceData", back_populates="device")

class DeviceData(Base):
    __tablename__ = "device_data"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, ForeignKey("devices.device_id"))
    heart_rate = Column(Integer)
    spo2 = Column(Integer)
    temperature = Column(Float)
    steps = Column(Integer)
    calories = Column(Integer)
    activity = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    device = relationship("UserDevice", back_populates="data")

# Create tables
Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()