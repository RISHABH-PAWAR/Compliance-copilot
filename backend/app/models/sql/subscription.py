"""Subscription Model"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Subscription(Base):
    """Company subscription plans and billing"""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    plan = Column(String(50), nullable=False)  # starter, professional, enterprise
    status = Column(String(20), default="active")  # active, paused, cancelled, expired
    
    # Pricing (INR)
    monthly_price = Column(Float, default=25000.0)
    setup_fee = Column(Float, default=15000.0)
    
    # Limits
    max_states = Column(Integer, default=1)
    max_employees = Column(Integer, default=250)
    max_users = Column(Integer, default=5)
    
    # Features
    has_api_access = Column(Boolean, default=False)
    has_slack_integration = Column(Boolean, default=False)
    has_custom_workflows = Column(Boolean, default=False)
    has_white_label = Column(Boolean, default=False)
    
    # Dates
    started_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Payment
    payment_method = Column(String(50), nullable=True)
    last_payment_at = Column(DateTime, nullable=True)
    next_billing_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="subscriptions")
