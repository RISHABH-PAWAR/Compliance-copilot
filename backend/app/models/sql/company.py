"""Company Model"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    registration_number = Column(String(100), unique=True, nullable=True)
    industry_type = Column(String(100), nullable=False)  # manufacturing, warehousing, services
    employee_count = Column(Integer, default=0)
    operational_states = Column(JSON, default=list)  # ["maharashtra", "gujarat", "tamil_nadu"]
    headquarters_state = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    gstin = Column(String(20), nullable=True)
    pan = Column(String(15), nullable=True)
    
    # Subscription
    subscription_plan = Column(String(50), default="starter")  # starter, professional, enterprise
    subscription_status = Column(String(20), default="active")
    
    # Settings
    notification_preferences = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="company")
    compliance_logs = relationship("ComplianceLog", back_populates="company")
    alerts = relationship("Alert", back_populates="company")
    subscriptions = relationship("Subscription", back_populates="company")
