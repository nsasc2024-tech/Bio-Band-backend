from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class AppUser(Base):
    __tablename__ = "app_users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    devices = relationship("UserDevice", back_populates="user")

class UserDevice(Base):
    __tablename__ = "user_devices"
    
    device_id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("app_users.user_id"), nullable=False)
    model = Column(String, nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("AppUser", back_populates="devices")
    data = relationship("DeviceData", back_populates="device")

class DeviceData(Base):
    __tablename__ = "device_data"
    
    data_id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, ForeignKey("user_devices.device_id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    heart_rate = Column(Integer)
    spo2 = Column(Integer)
    temperature = Column(Float)
    steps = Column(Integer)
    calories = Column(Integer)
    activity = Column(String)
    
    device = relationship("UserDevice", back_populates="data")