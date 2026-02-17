"""Report Schemas"""
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class ReportRequest(BaseModel):
    report_type: str  # compliance_summary, risk_assessment, audit_pack, financial_exposure
    format: str = "pdf"  # pdf, excel
    state_filter: Optional[str] = None
    regulation_filter: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class ReportResponse(BaseModel):
    id: str
    report_type: str
    format: str
    status: str  # generating, ready, failed
    generated_at: Optional[datetime] = None
    download_url: Optional[str] = None
    summary: Optional[Dict] = None


class DashboardData(BaseModel):
    """Aggregated dashboard data per role"""
    compliance_score: float  # 0-100
    total_gaps: int
    critical_gaps: int
    high_gaps: int
    medium_gaps: int
    low_gaps: int
    total_financial_exposure: float
    active_alerts: int
    pending_actions: int
    regulations_tracked: int
    recent_changes: int
    state_wise_risk: List[Dict]
    trend_data: List[Dict]
    recent_alerts: List[Dict]
    top_violations: List[Dict]
