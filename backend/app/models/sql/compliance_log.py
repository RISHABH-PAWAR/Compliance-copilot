"""Compliance Log Model"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class ComplianceLog(Base):
    """Tracks compliance analysis results per company per regulation"""
    __tablename__ = "compliance_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    regulation_rule_id = Column(Integer, ForeignKey("regulation_rules.id"), nullable=False)
    
    # Compliance Status
    status = Column(String(30), nullable=False)  # compliant, partial, violation, not_applicable
    gap_description = Column(Text, nullable=True)
    
    # Risk Score (Deterministic formula)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(20), default="low")  # low, medium, high, critical
    penalty_weight = Column(Float, default=0.0)
    inspection_frequency_score = Column(Float, default=0.0)
    employee_impact_scale = Column(Float, default=0.0)
    urgency_factor = Column(Float, default=0.0)
    
    # Financial
    estimated_penalty = Column(Float, default=0.0)
    estimated_cost_impact = Column(Float, default=0.0)
    
    # Resolution
    corrective_action = Column(Text, nullable=True)
    department_responsible = Column(String(100), nullable=True)
    documentation_needed = Column(JSON, default=list)
    deadline = Column(DateTime, nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, nullable=True)
    
    # Analysis metadata
    analyzed_by = Column(String(20), default="ai")  # ai, manual, hybrid
    confidence_score = Column(Float, default=0.0)
    legal_reference = Column(String(255), nullable=True)
    policy_document_id = Column(String(100), nullable=True)  # MongoDB ObjectId reference
    
    # Audit
    reviewed_by_legal = Column(Boolean, default=False)
    legal_review_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="compliance_logs")
    regulation_rule = relationship("RegulationRule")
