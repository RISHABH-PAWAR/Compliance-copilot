"""Alert Model"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Alert(Base):
    """Compliance alerts for companies"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    alert_type = Column(String(50), nullable=False)  # regulation_update, compliance_gap, deadline, inspection
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    
    # Reference
    regulation_id = Column(Integer, ForeignKey("regulations.id"), nullable=True)
    compliance_log_id = Column(Integer, ForeignKey("compliance_logs.id"), nullable=True)
    
    # State
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    action_required = Column(Boolean, default=True)
    action_url = Column(String(500), nullable=True)
    
    # Notification
    email_sent = Column(Boolean, default=False)
    slack_sent = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    company = relationship("Company", back_populates="alerts")
    regulation = relationship("Regulation")
