"""Compliance Schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ComplianceGap(BaseModel):
    id: int
    company_id: int
    regulation_rule_id: int
    rule_title: str
    act_name: str
    status: str  # compliant, partial, violation, not_applicable
    gap_description: Optional[str] = None
    risk_score: float
    risk_level: str  # low, medium, high, critical
    estimated_penalty: float
    estimated_cost_impact: float
    corrective_action: Optional[str] = None
    department_responsible: Optional[str] = None
    documentation_needed: List[str] = []
    deadline: Optional[datetime] = None
    resolved: bool = False
    legal_reference: Optional[str] = None
    analyzed_by: str = "ai"
    confidence_score: float = 0.0
    affected_employees: int = 0
    created_at: datetime


class ComplianceOverview(BaseModel):
    company_id: int
    total_rules_checked: int
    rules_checked: int  # Frontend match
    compliant: int
    partial: int
    violations: int
    not_applicable: int
    overall_score: float  # 0-100
    score: float  # Frontend match
    overall_risk_level: str
    total_financial_exposure: float
    total_gaps: int
    critical_gaps: int
    states: int = 1
    gaps: List[ComplianceGap]


class ComplianceChecklist(BaseModel):
    """Checklist item for corrective actions"""
    id: int
    rule_title: str
    act_name: str
    corrective_action: str
    department: str
    documentation_needed: List[str]
    deadline: Optional[datetime] = None
    priority: str  # low, medium, high, critical
    status: str  # pending, in_progress, completed
    inspection_readiness: bool = False


class ComplianceChecklistExport(BaseModel):
    company_name: str
    generated_at: datetime
    items: List[ComplianceChecklist]
    summary: dict


class RiskScoreBreakdown(BaseModel):
    penalty_weight: float
    inspection_frequency_score: float
    employee_impact_scale: float
    urgency_factor: float
    total_score: float
    risk_level: str


class StateComplianceMap(BaseModel):
    state: str
    total_rules: int
    compliant: int
    violations: int
    partial: int
    risk_level: str
    risk_score: float
    financial_exposure: float
