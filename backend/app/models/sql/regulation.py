"""Regulation & Regulation Rule Models"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Regulation(Base):
    """Top-level regulation/act (e.g., Factories Act, Minimum Wages Act)"""
    __tablename__ = "regulations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    act_name = Column(String(255), nullable=False, index=True)
    act_code = Column(String(50), unique=True, nullable=False)  # FACTORIES_ACT, MIN_WAGES, etc.
    category = Column(String(100), nullable=False)  # wages, safety, benefits, hours, etc.
    description = Column(Text, nullable=True)
    applicable_states = Column(JSON, default=list)  # ["all"] or specific states
    applicable_industries = Column(JSON, default=list)  # ["manufacturing", "services"]
    min_employee_threshold = Column(Integer, default=0)
    source_url = Column(String(500), nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    rules = relationship("RegulationRule", back_populates="regulation", cascade="all, delete-orphan")


class RegulationRule(Base):
    """Specific rule/section within a regulation"""
    __tablename__ = "regulation_rules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    regulation_id = Column(Integer, ForeignKey("regulations.id"), nullable=False)
    
    section_number = Column(String(50), nullable=True)
    rule_title = Column(String(500), nullable=False)
    rule_description = Column(Text, nullable=False)
    requirement = Column(Text, nullable=False)  # What the company must do
    
    # State-specific
    applicable_state = Column(String(100), default="all")
    
    # Compliance parameters
    penalty_amount = Column(Float, default=0.0)  # In INR
    penalty_description = Column(Text, nullable=True)
    inspection_frequency = Column(String(50), nullable=True)  # quarterly, annually, etc.
    documentation_required = Column(JSON, default=list)  # list of required documents
    employee_threshold = Column(Integer, default=0)
    
    # Risk parameters
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    urgency_factor = Column(Float, default=1.0)
    
    # Version tracking
    effective_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    previous_version_id = Column(Integer, ForeignKey("regulation_rules.id"), nullable=True)
    version = Column(Integer, default=1)
    change_summary = Column(Text, nullable=True)  # "What Changed?" diff data
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    regulation = relationship("Regulation", back_populates="rules")
    previous_version = relationship("RegulationRule", remote_side=[id])
