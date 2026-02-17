"""Audit Trail Model"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class AuditTrail(Base):
    """Immutable audit log for every significant action"""
    __tablename__ = "audit_trails"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    company_id = Column(Integer, nullable=True)
    
    action = Column(String(100), nullable=False)  # login, policy_upload, compliance_check, alert_dismiss, etc.
    resource_type = Column(String(100), nullable=True)  # policy, regulation, compliance_log, alert
    resource_id = Column(String(100), nullable=True)
    
    details = Column(JSON, default=dict)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    status = Column(String(20), default="success")  # success, failure, error
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_trails")
