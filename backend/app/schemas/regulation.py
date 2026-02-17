"""Regulation Schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class RegulationResponse(BaseModel):
    id: int
    act_name: str
    act_code: str
    category: str
    description: Optional[str] = None
    applicable_states: List[str]
    applicable_industries: List[str]
    min_employee_threshold: int
    source_url: Optional[str] = None
    last_updated: datetime
    rules_count: int = 0

    class Config:
        from_attributes = True


class RegulationRuleResponse(BaseModel):
    id: int
    regulation_id: int
    section_number: Optional[str] = None
    rule_title: str
    rule_description: str
    requirement: str
    applicable_state: str
    penalty_amount: float
    penalty_description: Optional[str] = None
    inspection_frequency: Optional[str] = None
    documentation_required: List[str]
    employee_threshold: int
    severity: str
    urgency_factor: float
    effective_date: Optional[datetime] = None
    version: int
    change_summary: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class RegulationDiff(BaseModel):
    """What Changed? diff data"""
    rule_id: int
    rule_title: str
    field: str
    old_value: str
    new_value: str
    change_date: datetime
    affected_departments: List[str] = []
    estimated_cost_impact: float = 0.0


class RegulationCreate(BaseModel):
    act_name: str
    act_code: str
    category: str
    description: Optional[str] = None
    applicable_states: List[str] = ["all"]
    applicable_industries: List[str] = ["all"]
    min_employee_threshold: int = 0
    source_url: Optional[str] = None


class RegulationRuleCreate(BaseModel):
    regulation_id: int
    section_number: Optional[str] = None
    rule_title: str
    rule_description: str
    requirement: str
    applicable_state: str = "all"
    penalty_amount: float = 0.0
    penalty_description: Optional[str] = None
    inspection_frequency: Optional[str] = None
    documentation_required: List[str] = []
    employee_threshold: int = 0
    severity: str = "medium"
    urgency_factor: float = 1.0
    effective_date: Optional[datetime] = None
